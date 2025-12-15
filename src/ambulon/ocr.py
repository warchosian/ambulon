#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module OCR pour Ambulon - Reconnaissance optique de caractères
"""

import argparse
import glob
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

def setup_logging(verbose: bool = False):
    """Configure le système de logging"""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%Hh%Mm%Ss")
    
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    log_file = logs_dir / f"ocr.{timestamp}.log"
    
    level = logging.DEBUG if verbose else logging.INFO
    
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    
    logging.basicConfig(
        level=level,
        handlers=[file_handler, console_handler],
        force=True
    )
    
    return log_file

# Imports optionnels
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

def perform_ocr(image_file: Path, language: str = 'fra', output_file: Path = None) -> Dict[str, Any]:
    """
    Effectue l'OCR sur un fichier image
    
    Args:
        image_file: Fichier image à traiter
        language: Langue pour l'OCR (défaut: 'fra')
        output_file: Fichier de sortie (optionnel)
        
    Returns:
        Dict contenant les informations sur l'OCR
    """
    try:
        # Charger la configuration pour obtenir le chemin de Tesseract
        import yaml
        import subprocess
        settings_file = Path("dk.config") / "settings.yaml"
        config = {}
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        
        # Vérifier la configuration de Tesseract
        tesseract_config = config.get('tools', {}).get('tesseract', {})
        tesseract_enabled = tesseract_config.get('enabled', True)
        tesseract_executable = tesseract_config.get('command', 'tesseract')
        
        # Vérifier s'il faut utiliser l'alternative Python
        if not tesseract_enabled:
            python_alt = tesseract_config.get('python_alternative')
            fallback_enabled = tesseract_config.get('fallback_enabled', False)
            
            if python_alt and fallback_enabled:
                logging.info(f"[FALLBACK] Tesseract désactivé, utilisation de l'alternative Python: {python_alt}")
                print(f"[FALLBACK] tesseract désactivé → utilisation de {python_alt}")
                return _perform_ocr_python(image_file, language, output_file)
            else:
                logging.error("[ERREUR] Tesseract désactivé et aucune alternative Python configurée")
                return {
                    'success': False,
                    'error': 'Tesseract désactivé et aucune alternative Python configurée'
                }
        
        # Générer le nom du fichier de sortie OCR
        if output_file is None:
            ocr_output_file = image_file.with_suffix('.txt')
        else:
            ocr_output_file = output_file
        
        logging.info(f"[OCR] Démarrage de l'OCR avec Tesseract")
        logging.info(f"[OCR] Exécutable : {tesseract_executable}")
        logging.info(f"[OCR] Langue : {language}")
        logging.info(f"[OCR] Fichier d'entrée : {image_file}")
        logging.info(f"[OCR] Fichier de sortie : {ocr_output_file}")
        
        # Construire la commande Tesseract
        # Tesseract ajoute automatiquement l'extension .txt
        output_base = str(ocr_output_file.with_suffix(''))
        
        cmd = [
            tesseract_executable,
            str(image_file),
            output_base,
            '-l', language,
            '--psm', '3',  # Page segmentation mode: Fully automatic page segmentation
            '--oem', '3'   # OCR Engine Mode: Default, based on what is available
        ]
        
        logging.info(f"[OCR] Commande : {' '.join(cmd)}")
        print(f"Lancement de l'OCR avec Tesseract...")
        print(f"Langue : {language}")
        print(f"Fichier de sortie OCR : {ocr_output_file}")
        
        # Exécuter la commande Tesseract
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True,
            timeout=60  # Timeout de 60 secondes pour l'OCR
        )
        
        # Vérifier que le fichier OCR a été créé
        if ocr_output_file.exists():
            ocr_size = ocr_output_file.stat().st_size
            logging.info(f"[OCR] OCR réussi : {ocr_output_file} ({ocr_size} octets)")
            print(f"Fichier OCR créé : {ocr_output_file}")
            print(f"Taille du fichier OCR : {ocr_size} octets")
            return {
                'success': True,
                'input_file': image_file,
                'output_file': ocr_output_file,
                'language': language,
                'file_size': ocr_size
            }
        else:
            logging.error(f"[OCR] Le fichier OCR n'a pas été créé : {ocr_output_file}")
            return {
                'success': False,
                'error': f'Le fichier OCR n\'a pas été créé : {ocr_output_file}'
            }
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Erreur Tesseract (code {e.returncode}): {e.stderr if e.stderr else 'Erreur inconnue'}"
        logging.error(f"[OCR] {error_msg}")
        print(f"Erreur OCR : {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
    except subprocess.TimeoutExpired:
        error_msg = "Timeout lors de l'OCR"
        logging.error(f"[OCR] {error_msg}")
        print(f"Erreur OCR : {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
    except FileNotFoundError:
        error_msg = f"Tesseract non trouvé : {tesseract_executable}"
        logging.error(f"[OCR] {error_msg}")
        print(f"Erreur OCR : {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
    except Exception as e:
        error_msg = f"Erreur générale OCR : {str(e)}"
        logging.error(f"[OCR] {error_msg}")
        print(f"Erreur OCR : {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }

def _perform_ocr_python(image_file: Path, language: str = 'fra', output_file: Path = None) -> Dict[str, Any]:
    """
    Effectue l'OCR avec pytesseract (alternative Python)
    
    Args:
        image_file: Fichier image à traiter
        language: Langue pour l'OCR (défaut: 'fra')
        output_file: Fichier de sortie (optionnel)
        
    Returns:
        Dict contenant les informations sur l'OCR
    """
    try:
        if not TESSERACT_AVAILABLE:
            logging.error("[OCR] pytesseract n'est pas disponible")
            return {
                'success': False,
                'error': 'pytesseract n\'est pas disponible'
            }
        
        import pytesseract
        from PIL import Image
        
        # Générer le nom du fichier de sortie OCR
        if output_file is None:
            ocr_output_file = image_file.with_suffix('.txt')
        else:
            ocr_output_file = output_file
        
        logging.info(f"[OCR] Démarrage de l'OCR avec pytesseract")
        logging.info(f"[OCR] Langue : {language}")
        logging.info(f"[OCR] Fichier d'entrée : {image_file}")
        logging.info(f"[OCR] Fichier de sortie : {ocr_output_file}")
        
        # Ouvrir l'image avec PIL
        with Image.open(image_file) as img:
            # Effectuer l'OCR
            text = pytesseract.image_to_string(img, lang=language)
        
        # Écrire le résultat dans le fichier
        with open(ocr_output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Vérifier que le fichier OCR a été créé
        if ocr_output_file.exists():
            ocr_size = ocr_output_file.stat().st_size
            logging.info(f"[OCR] OCR réussi avec pytesseract : {ocr_output_file} ({ocr_size} octets)")
            print(f"Fichier OCR créé avec pytesseract : {ocr_output_file}")
            print(f"Taille du fichier OCR : {ocr_size} octets")
            return {
                'success': True,
                'input_file': image_file,
                'output_file': ocr_output_file,
                'language': language,
                'file_size': ocr_size,
                'method': 'pytesseract'
            }
        else:
            logging.error(f"[OCR] Le fichier OCR n'a pas été créé : {ocr_output_file}")
            return {
                'success': False,
                'error': f'Le fichier OCR n\'a pas été créé : {ocr_output_file}'
            }
        
    except Exception as e:
        error_msg = f"Erreur pytesseract : {str(e)}"
        logging.error(f"[OCR] {error_msg}")
        print(f"Erreur OCR pytesseract : {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }

def process_multiple_files(file_pattern: str, language: str = 'fra', output_dir: Path = None, verbose: bool = False) -> Dict[str, Any]:
    """
    Traite plusieurs fichiers avec OCR
    
    Args:
        file_pattern: Pattern de fichiers (peut contenir des wildcards)
        language: Langue pour l'OCR
        output_dir: Répertoire de sortie (optionnel)
        verbose: Mode verbeux
        
    Returns:
        Dict contenant les résultats du traitement
    """
    logging.info(f"[OCR] Traitement de plusieurs fichiers : {file_pattern}")
    
    # Utiliser glob pour résoudre le pattern
    matching_files = glob.glob(file_pattern)
    
    if not matching_files:
        logging.warning(f"[OCR] Aucun fichier trouvé pour le pattern : {file_pattern}")
        return {
            'success': False,
            'error': f'Aucun fichier trouvé pour le pattern : {file_pattern}',
            'processed_files': []
        }
    
    logging.info(f"[OCR] {len(matching_files)} fichier(s) trouvé(s)")
    
    processed_files = []
    errors = []
    
    for file_path in matching_files:
        file_path = Path(file_path)
        logging.info(f"[OCR] Traitement de : {file_path}")
        
        try:
            # Déterminer le fichier de sortie
            if output_dir:
                output_file = output_dir / f"{file_path.stem}.txt"
            else:
                output_file = None
            
            # Effectuer l'OCR sur le fichier
            ocr_result = perform_ocr(file_path, language, output_file)
            
            if ocr_result['success']:
                processed_files.append({
                    'input_file': file_path,
                    'output_file': ocr_result['output_file'],
                    'success': True,
                    'file_size': ocr_result['file_size']
                })
                logging.info(f"[OCR] OCR réussi pour : {file_path}")
            else:
                errors.append(f"OCR échoué pour {file_path}: {ocr_result['error']}")
                logging.error(f"[OCR] OCR échoué pour : {file_path}")
                
        except Exception as e:
            error_msg = f"Erreur lors du traitement de {file_path}: {str(e)}"
            errors.append(error_msg)
            logging.error(f"[ERREUR] {error_msg}")
    
    success = len(processed_files) > 0
    
    return {
        'success': success,
        'processed_files': processed_files,
        'errors': errors,
        'total_files': len(matching_files),
        'successful_files': len(processed_files)
    }

def main():
    """Point d'entrée principal pour le module OCR"""
    parser = argparse.ArgumentParser(
        description='Module OCR pour Ambulon - Reconnaissance optique de caractères',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s -i image.jpg -l fra
  %(prog)s -i "scans/*.png" -l eng -o textes/
  %(prog)s -i document.pdf -l fra+eng -o resultat.txt
  %(prog)s -i "*.jpg" --batch -l fra

Langues supportées (exemples):
  fra - Français
  eng - Anglais
  deu - Allemand
  spa - Espagnol
  ita - Italien
  fra+eng - Français et Anglais combinés
        """
    )
    
    # Options principales
    parser.add_argument('-i', '--input', required=True,
                       help='Fichier d\'entrée ou pattern de fichiers (ex: image.jpg ou "*.png")')
    parser.add_argument('-o', '--output',
                       help='Fichier ou répertoire de sortie (optionnel)')
    parser.add_argument('-l', '--lang', default='fra',
                       help='Langue pour l\'OCR (défaut: fra)')
    
    # Options de traitement
    parser.add_argument('--batch', action='store_true',
                       help='Mode lot pour traiter plusieurs fichiers')
    parser.add_argument('--psm', type=int, choices=range(0, 14), default=3,
                       help='Page Segmentation Mode (0-13, défaut: 3)')
    parser.add_argument('--oem', type=int, choices=range(0, 4), default=3,
                       help='OCR Engine Mode (0-3, défaut: 3)')
    
    # Options de sortie
    parser.add_argument('--format', choices=['txt', 'pdf', 'hocr'], default='txt',
                       help='Format de sortie (défaut: txt)')
    parser.add_argument('--confidence', action='store_true',
                       help='Inclure les scores de confiance')
    
    # Options communes
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Mode verbeux')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Mode silencieux')
    parser.add_argument('--force', action='store_true',
                       help='Écraser les fichiers existants')
    
    args = parser.parse_args()
    
    # Configuration du logging
    log_file = setup_logging(args.verbose and not args.quiet)
    
    logging.info(f"[DÉMARRAGE] Démarrage du module OCR")
    logging.info(f"   Version Python : {sys.version}")
    logging.info(f"   Répertoire de travail : {Path.cwd()}")
    logging.info(f"   Langue OCR : {args.lang}")
    
    # Déterminer si c'est un traitement en lot
    input_str = str(args.input)
    has_wildcards = '*' in input_str or '?' in input_str
    
    if has_wildcards or args.batch:
        # Mode lot
        logging.info(f"[MODE] Mode lot détecté : {input_str}")
        
        output_dir = None
        if args.output:
            output_path = Path(args.output)
            if output_path.is_dir() or not output_path.suffix:
                output_dir = output_path
                output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            result = process_multiple_files(
                file_pattern=input_str,
                language=args.lang,
                output_dir=output_dir,
                verbose=args.verbose
            )
        except Exception as e:
            error_msg = f"Erreur lors du traitement en lot : {str(e)}"
            logging.error(f"[ERREUR] {error_msg}")
            print(f"Erreur : {error_msg}")
            return 1
    else:
        # Mode fichier unique
        logging.info(f"[MODE] Mode fichier unique : {input_str}")
        
        input_file = Path(args.input)
        if not input_file.exists():
            error_msg = f"Fichier d'entrée non trouvé : {input_file}"
            logging.error(f"[ERREUR] {error_msg}")
            print(f"Erreur : {error_msg}")
            return 1
        
        output_file = None
        if args.output:
            output_file = Path(args.output)
        
        try:
            result = perform_ocr(
                image_file=input_file,
                language=args.lang,
                output_file=output_file
            )
        except Exception as e:
            error_msg = f"Erreur lors de l'OCR : {str(e)}"
            logging.error(f"[ERREUR] {error_msg}")
            print(f"Erreur : {error_msg}")
            return 1
    
    # Afficher les résultats
    if result['success']:
        if 'processed_files' in result:
            # Mode lot
            if args.quiet:
                for file_info in result['processed_files']:
                    try:
                        relative_path = file_info['output_file'].relative_to(Path.cwd())
                        print(str(relative_path))
                    except ValueError:
                        print(str(file_info['output_file']))
            else:
                try:
                    from rich.console import Console
                    from rich.panel import Panel
                    
                    console = Console()
                    
                    # Construire le contenu du panneau de succès
                    content_lines = [
                        f"[green]OCR en lot réussi ![/green]\n",
                        f"[cyan]Fichiers traités :[/cyan] {result['successful_files']}/{result['total_files']}",
                        f"[cyan]Langue :[/cyan] {args.lang}"
                    ]
                    
                    content_lines.append("")
                    content_lines.append("[blue]Fichiers traités :[/blue]")
                    
                    # Lister tous les fichiers traités
                    for file_info in result['processed_files']:
                        try:
                            input_path = str(file_info['input_file'].relative_to(Path.cwd()))
                            output_path = str(file_info['output_file'].relative_to(Path.cwd()))
                        except ValueError:
                            input_path = str(file_info['input_file'])
                            output_path = str(file_info['output_file'])
                        
                        content_lines.append(f"[blue]✓[/blue] {input_path}")
                        content_lines.append(f"[blue]  → [/blue]{output_path} ({file_info['file_size']} octets)")
                    
                    # Afficher les erreurs s'il y en a
                    if result.get('errors'):
                        content_lines.append("")
                        content_lines.append("[yellow]Erreurs :[/yellow]")
                        for error in result['errors']:
                            content_lines.append(f"[red]✗[/red] {error}")
                    
                    success_panel = Panel(
                        "\n".join(content_lines),
                        title="[bold green]Succès[/bold green]",
                        border_style="green"
                    )
                    console.print(success_panel)
                    
                    try:
                        relative_log = log_file.relative_to(Path.cwd())
                        console.print(f"[dim]Log détaillé : {relative_log}[/dim]")
                    except ValueError:
                        console.print(f"[dim]Log détaillé : {log_file}[/dim]")
                        
                except ImportError:
                    print(f"OCR en lot réussi : {result['successful_files']}/{result['total_files']}")
                    print(f"  Langue : {args.lang}")
                    
                    for file_info in result['processed_files']:
                        print(f"  ✓ {file_info['input_file']}")
                        print(f"    → {file_info['output_file']} ({file_info['file_size']} octets)")
                    
                    if result.get('errors'):
                        print("  Erreurs :")
                        for error in result['errors']:
                            print(f"    ✗ {error}")
                    
                    try:
                        relative_log = log_file.relative_to(Path.cwd())
                        print(f"  Log détaillé : {relative_log}")
                    except ValueError:
                        print(f"  Log détaillé : {log_file}")
        else:
            # Mode fichier unique
            if args.quiet:
                try:
                    relative_path = result['output_file'].relative_to(Path.cwd())
                    print(str(relative_path))
                except ValueError:
                    print(str(result['output_file']))
            else:
                try:
                    from rich.console import Console
                    from rich.panel import Panel
                    
                    console = Console()
                    
                    try:
                        input_path = str(result['input_file'].relative_to(Path.cwd()))
                        output_path = str(result['output_file'].relative_to(Path.cwd()))
                    except ValueError:
                        input_path = str(result['input_file'])
                        output_path = str(result['output_file'])
                    
                    # Construire le contenu du panneau de succès
                    content_lines = [
                        f"[green]OCR réussi ![/green]\n",
                        f"[cyan]Langue :[/cyan] {result['language']}",
                        f"[cyan]Fichier d'entrée :[/cyan] {input_path}",
                        f"[cyan]Fichier de sortie :[/cyan] {output_path}",
                        f"[cyan]Taille :[/cyan] {result['file_size']} octets"
                    ]
                    
                    if result.get('method'):
                        content_lines.append(f"[cyan]Méthode :[/cyan] {result['method']}")
                    
                    success_panel = Panel(
                        "\n".join(content_lines),
                        title="[bold green]Succès[/bold green]",
                        border_style="green"
                    )
                    console.print(success_panel)
                    
                    try:
                        relative_log = log_file.relative_to(Path.cwd())
                        console.print(f"[dim]Log détaillé : {relative_log}[/dim]")
                    except ValueError:
                        console.print(f"[dim]Log détaillé : {log_file}[/dim]")
                        
                except ImportError:
                    print(f"OCR réussi !")
                    print(f"  Langue : {result['language']}")
                    print(f"  Fichier d'entrée : {result['input_file']}")
                    print(f"  Fichier de sortie : {result['output_file']}")
                    print(f"  Taille : {result['file_size']} octets")
                    
                    if result.get('method'):
                        print(f"  Méthode : {result['method']}")
                    
                    try:
                        relative_log = log_file.relative_to(Path.cwd())
                        print(f"  Log détaillé : {relative_log}")
                    except ValueError:
                        print(f"  Log détaillé : {log_file}")
        
        return 0
    else:
        if args.quiet:
            print(f"ERREUR: {result.get('error', 'Erreur inconnue')}")
        else:
            print(f"Erreur : {result.get('error', 'Erreur inconnue')}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
