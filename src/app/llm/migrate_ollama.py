#!/usr/bin/env python3
"""
🦙 Migration Avancée du Dépôt Ollama
• Cross-platform : Windows / Linux / macOS
• Détection auto de la source (OLLAMA_MODELS ou chemin par défaut)
• Barre de progression (tqdm si disponible, sinon fallback)
• Journalisation détaillée (fichier + console)
• Mode --dry-run pour tester sans rien modifier
• Création/écrasement garanti de OLLAMA_MODELS vers la destination
Python requis : ≥ 3.8
"""
import os
import sys
import shutil
import subprocess
import time
import platform
import logging
import argparse
from pathlib import Path

# ──────────────────────────────────────────────────────────────
# Dépendance optionnelle : tqdm
# ──────────────────────────────────────────────────────────────
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("ℹ️  tqdm non installé : utilisation d'une barre de progression simplifiée")
    print("💡 Pour une meilleure UX : pip install tqdm\n")

# ──────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────
def setup_logging(log_file: Path):
    """Configure la journalisation vers fichier et console."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    fmt = "%(asctime)s [%(levelname)s] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        datefmt=datefmt,
        handlers=[
            logging.FileHandler(log_file, mode='w', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# Utilitaires système
# ──────────────────────────────────────────────────────────────
def run_cmd(cmd, logger, ignore_errors=False, dry_run=False):
    """Exécute une commande système avec trace."""
    if dry_run:
        logger.info(f"[DRY-RUN] ▶ {cmd}")
        return True
    logger.info(f"▶ {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.stdout.strip():
        logger.debug(f"stdout: {res.stdout.strip()}")
    if res.stderr.strip():
        logger.warning(f"stderr: {res.stderr.strip()}")
    if res.returncode != 0 and not ignore_errors:
        logger.error(f"❌ Échec (code {res.returncode})")
        return False
    return True

def stop_ollama(logger, dry_run=False):
    """Arrête proprement tous les processus Ollama."""
    logger.info("🛑 Arrêt des processus Ollama...")
    system = platform.system()
    cmds = []
    if system == "Windows":
        cmds = ["taskkill /F /IM ollama.exe", "taskkill /F /IM Ollama.exe"]
    else:
        cmds = [
            "pkill -f ollama",
            "systemctl stop ollama 2>/dev/null",
            "launchctl unload ~/Library/LaunchAgents/com.ollama.ollama.plist 2>/dev/null"
        ]
    for c in cmds:
        run_cmd(c, logger, ignore_errors=True, dry_run=dry_run)
    if not dry_run:
        time.sleep(2)
    logger.info("✅ Processus arrêtés.")

def copy_with_progress(src: Path, dst: Path, logger, dry_run=False):
    """Copie récursive avec barre de progression et gestion d'erreurs."""
    logger.info(f"📦 Copie de {src} vers {dst}...")
    if dry_run:
        files = [f for f in src.rglob('*') if f.is_file()]
        size = sum(f.stat().st_size for f in files) / (1024**3)
        logger.info(f"[DRY-RUN] {len(files)} fichiers, {size:.2f} Go à copier")
        return True

    dst.mkdir(parents=True, exist_ok=True)
    files_to_copy = [(f, f.relative_to(src)) for f in src.rglob('*') if f.is_file()]
    total = len(files_to_copy)
    if total == 0:
        logger.warning("⚠️ Dossier source vide ou inaccessible.")
        return True

    logger.info(f"📊 {total} fichiers détectés")
    bar = tqdm(total=total, desc="Copie", unit="f") if HAS_TQDM else None
    errors = []

    for src_f, rel in files_to_copy:
        dst_f = dst / rel
        try:
            dst_f.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_f, dst_f)  # conserve timestamps & permissions
        except Exception as e:
            errors.append(f"{rel}: {e}")
            logger.error(f"❌ Échec: {rel}")
        if bar: bar.update(1)
        elif total > 0 and files_to_copy.index((src_f, rel)) % 10 == 0:
            print(f"  → {files_to_copy.index((src_f, rel))+1}/{total}...", end='\r')
    
    if bar: bar.close()
    else: print()
    
    if errors:
        logger.warning(f"⚠️ {len(errors)} erreurs (voir log)")
        return False
    logger.info("✅ Copie terminée.")
    return True

def set_persistent_env(path: str, logger, dry_run=False):
    """Définit OLLAMA_MODELS de façon persistante (session + OS)."""
    os.environ["OLLAMA_MODELS"] = path
    logger.info(f"⚙️ OLLAMA_MODELS défini sur : {path}")
    if dry_run:
        logger.info("[DRY-RUN] Variable non écrite de façon persistante")
        return

    system = platform.system()
    if system == "Windows":
        run_cmd(f'setx OLLAMA_MODELS "{path}"', logger)
        logger.info("✅ Variable écrite dans le registre utilisateur (HKCU)")
    else:
        line = f'export OLLAMA_MODELS="{path}"\n'
        for rc in [".zshrc", ".bashrc", ".profile", ".bash_profile"]:
            rc_path = Path.home() / rc
            if rc_path.exists():
                content = rc_path.read_text()
                if line.strip() not in content:
                    with open(rc_path, "a", encoding="utf-8") as f:
                        f.write(f"\n{line}")
                    logger.info(f"✅ Ajouté à ~/{rc}")
                break
        else:
            logger.warning("⚠️ Aucun fichier de shell trouvé. Ajoutez manuellement : export OLLAMA_MODELS=\"{}\"".format(path))

# ──────────────────────────────────────────────────────────────
# Point d'entrée principal
# ──────────────────────────────────────────────────────────────
def main():
    # Détection automatique de la source par défaut
    default_src = os.environ.get("OLLAMA_MODELS")
    if not default_src:
        if platform.system() == "Windows":
            default_src = os.path.join(os.environ.get("USERPROFILE", ""), ".ollama", "models")
        else:
            default_src = os.path.join(os.path.expanduser("~"), ".ollama", "models")

    parser = argparse.ArgumentParser(
        description="🦙 Migration du dépôt de modèles Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemples :\n"
            "  python %(prog)s \"z:\\nouveau\"                  # Source auto-détectée\n"
            "  python %(prog)s \"g:\\ancien\" \"z:\\nouveau\"      # Source explicite\n"
            "  python %(prog)s \"z:\\nouveau\" --dry-run        # Simulation sans modification"
        )
    )
    parser.add_argument("source", nargs="?", default=default_src,
                        help="Dossier source (défaut : $OLLAMA_MODELS ou chemin officiel)")
    parser.add_argument("destination", help="Dossier de destination")
    parser.add_argument("--dry-run", action="store_true", help="Simulation sans toucher aux fichiers")
    parser.add_argument("--log", type=str, default=None, help="Chemin personnalisé du fichier de log")
    
    args = parser.parse_args()
    src = Path(args.source).resolve()
    dst = Path(args.destination).resolve()
    log_path = Path(args.log) if args.log else Path("ollama_migration.log")

    logger = setup_logging(log_path)
    mode = "🧪 DRY-RUN - " if args.dry_run else ""
    logger.info(f"{mode}Migration démarrée")
    logger.info(f"📥 Source : {src}")
    logger.info(f"📤 Cible  : {dst}")
    logger.info(f"📝 Log    : {log_path.resolve()}")
    logger.info(f"🖥️  OS    : {platform.system()} {platform.release()}\n")

    # Validations
    if not src.exists():
        logger.error(f"❌ Dossier source introuvable : {src}")
        logger.info("💡 Vérifiez le chemin ou définissez OLLAMA_MODELS")
        sys.exit(1)
    if src == dst:
        logger.error("❌ Source et destination identiques !")
        sys.exit(1)

    # 1. Arrêt Ollama
    stop_ollama(logger, args.dry_run)

    # 2. Copie
    if not copy_with_progress(src, dst, logger, args.dry_run):
        logger.error("❌ Migration interrompue : erreurs de copie")
        sys.exit(1)

    # 3. Nettoyage source
    if not args.dry_run:
        logger.info("🗑️ Suppression de la source...")
        try:
            shutil.rmtree(src)
            logger.info("✅ Ancien dossier supprimé.")
        except PermissionError:
            logger.warning("⚠️ Fichiers encore verrouillés. Supprimez manuellement après redémarrage.")
        except Exception as e:
            logger.error(f"❌ Erreur suppression : {e}")
    else:
        logger.info("[DRY-RUN] Source conservée")

    # 4. Variable d'environnement (TOUJOURS créée/écrasée)
    set_persistent_env(str(dst), logger, args.dry_run)

    # Résumé
    sep = "═" * 60
    logger.info("\n" + sep)
    if args.dry_run:
        logger.info("🧪 SIMULATION TERMINÉE - Aucune modification appliquée")
        logger.info("💡 Relancez sans --dry-run pour appliquer")
    else:
        logger.info("✨ MIGRATION TERMINÉE AVEC SUCCÈS !")
        logger.info("🔑 Prochaines étapes obligatoires :")
        logger.info("   1. Fermez TOUS les terminaux / applications")
        logger.info("   2. Ouvrez un NOUVEAU terminal")
        logger.info("   3. Vérifiez : echo $OLLAMA_MODELS  (ou %OLLAMA_MODELS% sous Win)")
        logger.info("   4. Testez   : ollama list")
        logger.info("   5. Lancez   : ollama serve (ou relancez l'app Ollama)")
    logger.info(sep)

if __name__ == "__main__":
    main()