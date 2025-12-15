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

def perform_ocr(input_path: Path, language: str = 'fra', output_path: Path = None) -> Dict[str, Any]:
    """
    Effectue l'OCR sur un fichier image ou un dossier
    
    Args:
        input_path: Fichier image ou dossier à traiter
        language: Langue pour l'OCR (défaut: 'fra')
        output_path: Fichier ou dossier de sortie (optionnel)
        
    Returns:
        Dict contenant les informations sur l'OCR
    """
    # Vérifier que le chemin d'entrée existe
    if not input_path.exists():
        return {
            'success': False,
            'error': f'Chemin non trouvé : {input_path}'
        }
    
    # Si c'est un dossier, traiter tous les fichiers
    if input_path.is_dir():
        return _process_directory_ocr(input_path, language, output_path)
    
    # Si c'est un fichier, traiter le fichier unique
    file_size = input_path.stat().st_size
    if file_size == 0:
        return {
            'success': False,
            'error': f'Le fichier est vide (0 octets) : {input_path}'
        }
    
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
                return _perform_ocr_python(input_path, language, output_path)
            else:
                logging.error("[ERREUR] Tesseract désactivé et aucune alternative Python configurée")
                return {
                    'success': False,
                    'error': 'Tesseract désactivé et aucune alternative Python configurée'
                }
        
        # Générer le nom du fichier de sortie OCR
        if output_path is None:
            ocr_output_file = input_path.with_suffix('.txt')
        else:
            ocr_output_file = output_path
        
        logging.info(f"[OCR] Démarrage de l'OCR avec Tesseract")
        logging.info(f"[OCR] Exécutable : {tesseract_executable}")
        logging.info(f"[OCR] Langue : {language}")
        logging.info(f"[OCR] Fichier d'entrée : {input_path}")
        logging.info(f"[OCR] Fichier de sortie : {ocr_output_file}")
        
        # Construire la commande Tesseract
        # Tesseract ajoute automatiquement l'extension .txt
        output_base = str(ocr_output_file.with_suffix(''))
        
        cmd = [
            tesseract_executable,
            str(input_path),
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
                'input_file': input_path,
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

def _process_directory_ocr(directory: Path, language: str = 'fra', output_dir: Path = None) -> Dict[str, Any]:
    """
    Traite tous les fichiers images et PDF d'un dossier avec OCR
    
    Args:
        directory: Dossier contenant les fichiers à traiter
        language: Langue pour l'OCR
        output_dir: Dossier de sortie (optionnel)
        
    Returns:
        Dict contenant les résultats du traitement
    """
    # Extensions supportées pour l'OCR
    supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.pdf'}
    
    # Trouver tous les fichiers supportés dans le dossier
    files_to_process = []
    for file_path in directory.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            files_to_process.append(file_path)
    
    if not files_to_process:
        return {
            'success': False,
            'error': f'Aucun fichier image ou PDF trouvé dans {directory}',
            'processed_files': []
        }
    
    logging.info(f"[OCR] Traitement du dossier : {directory}")
    logging.info(f"[OCR] {len(files_to_process)} fichier(s) trouvé(s)")
    
    # Déterminer le dossier de sortie
    if output_dir is None:
        output_dir = directory / "textes"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    processed_files = []
    errors = []
    
    for file_path in files_to_process:
        try:
            logging.info(f"[OCR] Traitement de : {file_path}")
            
            # Déterminer le fichier de sortie
            output_file = output_dir / f"{file_path.stem}.txt"
            
            # Traiter selon le type de fichier
            if file_path.suffix.lower() == '.pdf':
                # Pour les PDF, extraire d'abord les images puis faire l'OCR
                result = _process_pdf_ocr(file_path, language, output_file)
            else:
                # Pour les images, OCR direct
                result = perform_ocr_single_file(file_path, language, output_file)
            
            if result['success']:
                processed_files.append({
                    'input_file': file_path,
                    'output_file': result['output_file'],
                    'success': True,
                    'file_size': result['file_size']
                })
                logging.info(f"[OCR] OCR réussi pour : {file_path}")
            else:
                errors.append(f"OCR échoué pour {file_path}: {result['error']}")
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
        'total_files': len(files_to_process),
        'successful_files': len(processed_files),
        'output_directory': output_dir
    }


def _process_pdf_ocr(pdf_file: Path, language: str = 'fra', output_file: Path = None) -> Dict[str, Any]:
    """
    Effectue l'OCR sur un fichier PDF en extrayant d'abord les images
    
    Args:
        pdf_file: Fichier PDF à traiter
        language: Langue pour l'OCR
        output_file: Fichier de sortie (optionnel)
        
    Returns:
        Dict contenant les informations sur l'OCR
    """
    try:
        import fitz  # PyMuPDF
        
        # Générer le nom du fichier de sortie OCR
        if output_file is None:
            ocr_output_file = pdf_file.with_suffix('.txt')
        else:
            ocr_output_file = output_file
        
        logging.info(f"[OCR] Traitement PDF : {pdf_file}")
        
        # Ouvrir le PDF
        doc = fitz.open(pdf_file)
        all_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # D'abord essayer d'extraire le texte directement
            text = page.get_text()
            if text.strip():
                all_text.append(f"=== Page {page_num + 1} (texte direct) ===\n{text}\n")
                logging.info(f"[OCR] Page {page_num + 1}: texte extrait directement")
            else:
                # Si pas de texte, convertir en image et faire l'OCR
                logging.info(f"[OCR] Page {page_num + 1}: conversion en image pour OCR")
                
                # Rendre la page en image
                mat = fitz.Matrix(2.0, 2.0)  # Zoom 2x pour meilleure qualité OCR
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Sauvegarder temporairement l'image
                temp_image = pdf_file.parent / f"temp_page_{page_num + 1}.png"
                pix.save(temp_image)
                
                try:
                    # Faire l'OCR sur l'image temporaire
                    temp_output = pdf_file.parent / f"temp_page_{page_num + 1}.txt"
                    ocr_result = perform_ocr_single_file(temp_image, language, temp_output)
                    
                    if ocr_result['success'] and temp_output.exists():
                        with open(temp_output, 'r', encoding='utf-8') as f:
                            page_text = f.read()
                        all_text.append(f"=== Page {page_num + 1} (OCR) ===\n{page_text}\n")
                        
                        # Nettoyer les fichiers temporaires
                        temp_output.unlink(missing_ok=True)
                    
                    temp_image.unlink(missing_ok=True)
                    
                except Exception as e:
                    logging.warning(f"[OCR] Erreur OCR page {page_num + 1}: {e}")
                    all_text.append(f"=== Page {page_num + 1} (erreur OCR) ===\nErreur: {e}\n")
        
        doc.close()
        
        # Écrire tout le texte dans le fichier de sortie
        combined_text = "\n".join(all_text)
        with open(ocr_output_file, 'w', encoding='utf-8') as f:
            f.write(combined_text)
        
        ocr_size = ocr_output_file.stat().st_size
        logging.info(f"[OCR] OCR PDF réussi : {ocr_output_file} ({ocr_size} octets)")
        
        return {
            'success': True,
            'input_file': pdf_file,
            'output_file': ocr_output_file,
            'language': language,
            'file_size': ocr_size,
            'pages_processed': len(doc)
        }
        
    except ImportError:
        return {
            'success': False,
            'error': 'PyMuPDF non installé. Installez avec: pip install PyMuPDF'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Erreur lors du traitement PDF: {str(e)}'
        }


def perform_ocr_single_file(image_file: Path, language: str = 'fra', output_file: Path = None) -> Dict[str, Any]:
    """
    Effectue l'OCR sur un fichier image unique
    
    Args:
        image_file: Fichier image à traiter
        language: Langue pour l'OCR (défaut: 'fra')
        output_file: Fichier de sortie (optionnel)
        
    Returns:
        Dict contenant les informations sur l'OCR
    """
    # Vérifier que le fichier existe et n'est pas vide
    if not image_file.exists():
        return {
            'success': False,
            'error': f'Fichier image non trouvé : {image_file}'
        }
    
    file_size = image_file.stat().st_size
    if file_size == 0:
        return {
            'success': False,
            'error': f'Le fichier image est vide (0 octets) : {image_file}'
        }
    
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


def _process_pdf_ocr(pdf_file: Path, language: str = 'fra', output_file: Path = None) -> Dict[str, Any]:
    """
    Effectue l'OCR sur un fichier PDF en extrayant d'abord les images
    
    Args:
        pdf_file: Fichier PDF à traiter
        language: Langue pour l'OCR
        output_file: Fichier de sortie (optionnel)
        
    Returns:
        Dict contenant les informations sur l'OCR
    """
    try:
        import fitz  # PyMuPDF
        
        # Générer le nom du fichier de sortie OCR
        if output_file is None:
            ocr_output_file = pdf_file.with_suffix('.txt')
        else:
            ocr_output_file = output_file
        
        logging.info(f"[OCR] Traitement PDF : {pdf_file}")
        
        # Ouvrir le PDF
        doc = fitz.open(pdf_file)
        all_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # D'abord essayer d'extraire le texte directement
            text = page.get_text()
            if text.strip():
                all_text.append(f"=== Page {page_num + 1} (texte direct) ===\n{text}\n")
                logging.info(f"[OCR] Page {page_num + 1}: texte extrait directement")
            else:
                # Si pas de texte, convertir en image et faire l'OCR
                logging.info(f"[OCR] Page {page_num + 1}: conversion en image pour OCR")
                
                # Rendre la page en image
                mat = fitz.Matrix(2.0, 2.0)  # Zoom 2x pour meilleure qualité OCR
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Sauvegarder temporairement l'image
                temp_image = pdf_file.parent / f"temp_page_{page_num + 1}.png"
                pix.save(temp_image)
                
                try:
                    # Faire l'OCR sur l'image temporaire
                    temp_output = pdf_file.parent / f"temp_page_{page_num + 1}.txt"
                    ocr_result = perform_ocr_single_file(temp_image, language, temp_output)
                    
                    if ocr_result['success'] and temp_output.exists():
                        with open(temp_output, 'r', encoding='utf-8') as f:
                            page_text = f.read()
                        all_text.append(f"=== Page {page_num + 1} (OCR) ===\n{page_text}\n")
                        
                        # Nettoyer les fichiers temporaires
                        temp_output.unlink(missing_ok=True)
                    
                    temp_image.unlink(missing_ok=True)
                    
                except Exception as e:
                    logging.warning(f"[OCR] Erreur OCR page {page_num + 1}: {e}")
                    all_text.append(f"=== Page {page_num + 1} (erreur OCR) ===\nErreur: {e}\n")
        
        doc.close()
        
        # Écrire tout le texte dans le fichier de sortie
        combined_text = "\n".join(all_text)
        with open(ocr_output_file, 'w', encoding='utf-8') as f:
            f.write(combined_text)
        
        ocr_size = ocr_output_file.stat().st_size
        logging.info(f"[OCR] OCR PDF réussi : {ocr_output_file} ({ocr_size} octets)")
        
        return {
            'success': True,
            'input_file': pdf_file,
            'output_file': ocr_output_file,
            'language': language,
            'file_size': ocr_size,
            'pages_processed': len(doc)
        }
        
    except ImportError:
        return {
            'success': False,
            'error': 'PyMuPDF non installé. Installez avec: pip install PyMuPDF'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Erreur lors du traitement PDF: {str(e)}'
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
            if file_path.is_dir():
                ocr_result = _process_directory_ocr(file_path, language, output_file.parent if output_file else None)
            else:
                ocr_result = perform_ocr_single_file(file_path, language, output_file)
            
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
  %(prog)s -i dossier_images/ -l fra -o textes/
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
                       help='Fichier, dossier ou pattern de fichiers (ex: image.jpg, dossier/, "*.png")')
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
    
    # Déterminer le type de traitement
    input_str = str(args.input)
    input_path = Path(args.input)
    has_wildcards = '*' in input_str or '?' in input_str
    
    # Vérifier d'abord si le chemin existe
    if not input_path.exists() and not has_wildcards:
        error_msg = f"Chemin d'entrée non trouvé : {input_path}"
        logging.error(f"[ERREUR] {error_msg}")
        print(f"Erreur : {error_msg}")
        return 1
    
    # Détecter le type de traitement en priorité sur l'existence du chemin
    if input_path.exists() and input_path.is_dir():
        # Mode dossier - traiter tous les fichiers du dossier
        logging.info(f"[MODE] Mode dossier détecté : {input_str}")
        
        output_dir = None
        if args.output:
            output_path = Path(args.output)
            if output_path.is_dir() or not output_path.suffix:
                output_dir = output_path
            else:
                # Si c'est un fichier, utiliser son dossier parent
                output_dir = output_path.parent
                output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            result = _process_directory_ocr(
                directory=input_path,
                language=args.lang,
                output_dir=output_dir
            )
        except Exception as e:
            error_msg = f"Erreur lors du traitement du dossier : {str(e)}"
            logging.error(f"[ERREUR] {error_msg}")
            print(f"Erreur : {error_msg}")
            return 1
    elif has_wildcards or args.batch:
        # Mode lot avec pattern
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
    elif input_path.exists() and input_path.is_file():
        # Mode fichier unique - traiter le fichier spécifique
        logging.info(f"[MODE] Mode fichier unique : {input_str}")
        
        output_file = None
        if args.output:
            output_file = Path(args.output)
        
        try:
            result = perform_ocr_single_file(
                image_file=input_path,
                language=args.lang,
                output_file=output_file
            )
        except Exception as e:
            error_msg = f"Erreur lors de l'OCR : {str(e)}"
            logging.error(f"[ERREUR] {error_msg}")
            print(f"Erreur : {error_msg}")
            return 1
    else:
        error_msg = f"Le chemin '{input_path}' n'est ni un fichier ni un dossier valide"
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
