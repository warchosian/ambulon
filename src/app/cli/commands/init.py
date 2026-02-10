"""Commande d'initialisation pour générer les fichiers de configuration."""

import sys
from pathlib import Path
from typing import Optional


def create_config_file(module: str, config_dir: Path, force: bool = False) -> bool:
    """
    Crée un fichier de configuration à partir du template embarqué.

    Args:
        module: Nom du module (piag, gitlab, wikisi)
        config_dir: Répertoire où créer le fichier
        force: Écraser le fichier s'il existe déjà

    Returns:
        True si le fichier a été créé, False sinon
    """
    # Mapper module vers template
    module_templates = {
        'piag': ('app.piag.core.config_template', 'PIAG_CONFIG_TEMPLATE'),
        'gitlab': ('app.gitlab.core.config_template', 'GITLAB_CONFIG_TEMPLATE'),
        'wikisi': ('app.wikisi.core.config_template', 'WIKISI_CONFIG_TEMPLATE'),
    }

    if module not in module_templates:
        print(f"❌ Module inconnu: {module}")
        print(f"   Modules disponibles: {', '.join(module_templates.keys())}")
        return False

    # Obtenir le template
    module_path, template_name = module_templates[module]
    try:
        import importlib
        template_module = importlib.import_module(module_path)
        template_content = getattr(template_module, template_name)
    except ImportError:
        print(f"❌ Impossible d'importer le module {module_path}")
        return False
    except AttributeError:
        print(f"❌ Template {template_name} introuvable dans {module_path}")
        return False

    # Créer le fichier de configuration
    config_file = config_dir / f"{module}.yaml"

    if config_file.exists() and not force:
        print(f"⚠️  Le fichier existe déjà: {config_file}")
        print(f"   Utilisez --force pour écraser")
        return False

    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file.write_text(template_content, encoding='utf-8')
        print(f"✅ Fichier créé: {config_file}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création de {config_file}: {e}")
        return False


def handle_init_command():
    """Gère la commande ambulon init."""
    if len(sys.argv) < 3:
        print("Usage: ambulon init [MODULE|--all] [OPTIONS]")
        print()
        print("Arguments:")
        print("  MODULE        Nom du module (piag, gitlab, wikisi)")
        print("  --all         Initialiser tous les modules")
        print()
        print("Options:")
        print("  --force       Écraser les fichiers existants")
        print("  --config-dir  Répertoire de configuration (défaut: config/)")
        print("  -h, --help    Afficher cette aide")
        print()
        print("Exemples:")
        print("  ambulon init piag              Créer config/piag.yaml")
        print("  ambulon init --all             Créer tous les fichiers de config")
        print("  ambulon init gitlab --force    Écraser config/gitlab.yaml")
        print()
        print("Description:")
        print("  Cette commande génère les fichiers de configuration YAML à partir")
        print("  des templates embarqués dans le package Ambulon. Les fichiers créés")
        print("  contiennent des exemples et des commentaires pour vous guider.")
        print()
        print("  Après génération, éditez les fichiers pour remplir vos credentials:")
        print("    - config/piag.yaml    : Token API RAG, project_id")
        print("    - config/gitlab.yaml  : Token GitLab, repositories")
        print("    - config/wikisi.yaml  : URL du site, options d'aspiration")
        return 1

    # Parser les arguments
    module = sys.argv[2]
    force = '--force' in sys.argv

    # Déterminer le répertoire de config
    config_dir = Path("config")
    if '--config-dir' in sys.argv:
        idx = sys.argv.index('--config-dir')
        if idx + 1 < len(sys.argv):
            config_dir = Path(sys.argv[idx + 1])

    # Gérer l'aide
    if module in ['-h', '--help']:
        print("Usage: ambulon init [MODULE|--all] [OPTIONS]")
        print()
        print("Arguments:")
        print("  MODULE        Nom du module (piag, gitlab, wikisi)")
        print("  --all         Initialiser tous les modules")
        print()
        print("Options:")
        print("  --force       Écraser les fichiers existants")
        print("  --config-dir  Répertoire de configuration (défaut: config/)")
        print("  -h, --help    Afficher cette aide")
        print()
        print("Exemples:")
        print("  ambulon init piag              Créer config/piag.yaml")
        print("  ambulon init --all             Créer tous les fichiers de config")
        print("  ambulon init gitlab --force    Écraser config/gitlab.yaml")
        return 0

    # Exécuter la création
    if module == '--all':
        print("📦 Initialisation de toutes les configurations...")
        print()
        modules = ['piag', 'gitlab', 'wikisi']
        success_count = 0

        for mod in modules:
            if create_config_file(mod, config_dir, force):
                success_count += 1

        print()
        print(f"✅ {success_count}/{len(modules)} fichiers créés avec succès")
        print()
        print("📝 Prochaines étapes:")
        print(f"  1. Éditez les fichiers dans {config_dir}/")
        print("  2. Remplissez vos credentials (tokens, project IDs, etc.)")
        print("  3. Les fichiers de config sont dans .gitignore (pas de commit accidentel)")
        print()
        print("⚠️  Important: Ne commitez JAMAIS vos tokens dans Git !")

        return 0 if success_count == len(modules) else 1

    else:
        # Initialiser un module spécifique
        print(f"📦 Initialisation de la configuration {module}...")
        print()

        if create_config_file(module, config_dir, force):
            print()
            print("📝 Prochaines étapes:")
            print(f"  1. Éditez {config_dir}/{module}.yaml")
            print("  2. Remplissez vos credentials")
            print("  3. Consultez la documentation du module pour plus de détails")
            print()
            print(f"⚠️  Ce fichier est dans .gitignore (pas de commit)")
            return 0
        else:
            return 1
