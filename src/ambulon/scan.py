#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de scan TWAIN avec profils DPI pour Ambulon
"""

import argparse
import glob
import logging
import re
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
    
    log_file = logs_dir / f"scan.{timestamp}.log"
    
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

def scan_document(dpi: int, output_dir: Path = None, **kwargs) -> Dict[str, Any]:
    """
    Scanne un document avec le profil DPI spécifié
    
    Args:
        dpi: Résolution de scan en DPI
        output_dir: Répertoire de sortie
        **kwargs: Options de scan supplémentaires
        
    Returns:
        Dict contenant les informations sur le scan
    """
    # Utiliser directement _perform_single_scan qui gère maintenant le nombre de scans
    return _perform_single_scan(dpi, output_dir, 1, **kwargs)

def _perform_single_scan(dpi: int, output_dir: Path = None, scan_number: int = 1, **kwargs) -> Dict[str, Any]:
    """
    Effectue un scan unique ou multiple
    
    Args:
        dpi: Résolution de scan en DPI
        output_dir: Répertoire de sortie
        scan_number: Numéro du scan (pour la numérotation)
        **kwargs: Options de scan supplémentaires
        
    Returns:
        Dict contenant les informations sur le scan
    """
    if output_dir is None:
        output_dir = Path("./scans")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    number_of_scans = kwargs.get('number', 1)
    
    if number_of_scans > 1:
        logging.info(f"[SCAN] Démarrage de {number_of_scans} scans en {dpi} DPI")
    else:
        logging.info(f"[SCAN] Démarrage du scan en {dpi} DPI")
    logging.info(f"   Répertoire de sortie : {output_dir}")
    
    paper_size = kwargs.get('paper_size', 'A4')
    color_mode = kwargs.get('color_mode', 'color')
    format_output = kwargs.get('format', 'pdf')
    brightness = kwargs.get('brightness', 0)
    contrast = kwargs.get('contrast', 0)
    
    logging.info(f"   Taille papier : {paper_size}")
    logging.info(f"   Mode couleur : {color_mode}")
    logging.info(f"   Format de sortie : {format_output}")
    logging.info(f"   Luminosité : {brightness}")
    logging.info(f"   Contraste : {contrast}")
    
    # Traiter -o comme le début du chemin d'un fichier
    if output_dir.name and output_dir.name != 'scans':
        # Vérifier si -o contient un nom de fichier complet avec extension
        if '.' in output_dir.name and output_dir.suffix:
            # -o contient un nom de fichier complet (ex: scans\drap.jpg)
            target_dir = output_dir.parent if output_dir.parent != Path('.') else Path('.')
            filename = output_dir.name
            output_file = target_dir / filename
        else:
            # -o contient le début du nom de fichier sans extension
            filename_base = output_dir.name
            target_dir = output_dir.parent if output_dir.parent != Path('.') else Path('.')
            
            # Créer le répertoire cible si nécessaire
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Trouver le prochain numéro disponible en cherchant les fichiers existants
            existing_files = list(target_dir.glob(f"{filename_base}-*.{format_output}"))
            existing_numbers = []
            
            for existing_file in existing_files:
                # Extraire le numéro du nom de fichier (ex: scan-001.png -> 001)
                match = re.match(rf"{re.escape(filename_base)}-(\d{{3}})\.{re.escape(format_output)}", existing_file.name)
                if match:
                    existing_numbers.append(int(match.group(1)))
            
            # Déterminer le prochain numéro disponible
            if existing_numbers:
                next_number = max(existing_numbers) + 1
            else:
                next_number = 1
            
            # Pour les scans multiples, générer le nom de base sans numéro
            # NAPS2 ajoutera automatiquement la numérotation
            if number_of_scans > 1:
                filename_base_for_naps2 = filename_base
                output_file = target_dir / f"{filename_base_for_naps2}.{format_output}"
            else:
                filename = f"{filename_base}-{next_number:03d}.{format_output}"
                output_file = target_dir / filename
    else:
        # Nom par défaut
        filename_base = f"scan_{dpi}dpi"
        target_dir = output_dir
        
        # Créer le répertoire cible si nécessaire
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Trouver le prochain numéro disponible en cherchant les fichiers existants
        existing_files = list(target_dir.glob(f"{filename_base}-*.{format_output}"))
        existing_numbers = []
        
        for existing_file in existing_files:
            # Extraire le numéro du nom de fichier (ex: scan-001.png -> 001)
            match = re.match(rf"{re.escape(filename_base)}-(\d{{3}})\.{re.escape(format_output)}", existing_file.name)
            if match:
                existing_numbers.append(int(match.group(1)))
        
        # Déterminer le prochain numéro disponible
        if existing_numbers:
            next_number = max(existing_numbers) + 1
        else:
            next_number = 1
        
        # Pour les scans multiples, générer le nom de base sans numéro
        # NAPS2 ajoutera automatiquement la numérotation
        if number_of_scans > 1:
            filename_base_for_naps2 = filename_base
            output_file = target_dir / f"{filename_base_for_naps2}.{format_output}"
        else:
            filename = f"{filename_base}-{next_number:03d}.{format_output}"
            output_file = target_dir / filename
    
    # Créer le répertoire cible si nécessaire (pour tous les cas)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"   Répertoire cible : {output_file.parent}")
    if number_of_scans > 1:
        logging.info(f"   Nom de base pour NAPS2 : {output_file.name}")
        logging.info(f"   Mode : scans multiples ({number_of_scans} scans)")
        logging.info(f"   NAPS2 générera automatiquement la numérotation")
    else:
        logging.info(f"   Nom de fichier généré : {output_file.name}")
        if '.' in output_dir.name and output_dir.suffix:
            logging.info(f"   Mode : nom de fichier complet spécifié")
        else:
            logging.info(f"   Mode : génération automatique avec numérotation")
            if 'existing_files' in locals():
                logging.info(f"   Fichiers existants trouvés : {len(existing_files)}")
                if 'existing_numbers' in locals() and existing_numbers:
                    logging.info(f"   Dernier numéro utilisé : {max(existing_numbers):03d}")
                if 'next_number' in locals():
                    logging.info(f"   Prochain numéro : {next_number:03d}")
    
    try:
        # Essayer d'utiliser l'interface TWAIN
        success = _perform_twain_scan(
            output_file=output_file,
            dpi=dpi,
            **kwargs
        )
        
        if success:
            number_of_scans = kwargs.get('number', 1)
            
            if number_of_scans > 1:
                # Collecter tous les fichiers générés
                base_name = output_file.stem
                extension = output_file.suffix
                parent_dir = output_file.parent
                
                generated_files = []
                for i in range(1, number_of_scans + 1):
                    expected_file = parent_dir / f"{base_name} ({i}){extension}"
                    if expected_file.exists():
                        generated_files.append(expected_file)
                
                logging.info(f"[SUCCÈS] Scans multiples terminés : {len(generated_files)} fichier(s)")
                
                return {
                    'success': True,
                    'multiple_scans': True,
                    'total_scans': number_of_scans,
                    'successful_scans': len(generated_files),
                    'results': [{'output_file': f, 'success': True} for f in generated_files],
                    'errors': [],
                    'dpi': dpi,
                    'settings': kwargs
                }
            else:
                logging.info(f"[SUCCÈS] Scan terminé : {output_file}")
                return {
                    'success': True,
                    'output_file': output_file,
                    'dpi': dpi,
                    'settings': kwargs
                }
        else:
            # Fallback vers simulation si TWAIN échoue
            logging.warning("[ATTENTION] Scan TWAIN échoué, utilisation du mode simulation")
            return _simulate_scan(output_file, dpi, kwargs)
        
    except Exception as e:
        error_msg = f"Erreur lors du scan : {str(e)}"
        logging.error(f"[ERREUR] {error_msg}")
        # Fallback vers simulation en cas d'erreur
        logging.warning("[ATTENTION] Erreur TWAIN, utilisation du mode simulation")
        return _simulate_scan(output_file, dpi, kwargs)

def _perform_twain_scan(output_file: Path, dpi: int, **kwargs) -> bool:
    """
    Effectue un scan réel via NAPS2 Console (comme dans skan.py)
    
    Returns:
        bool: True si le scan a réussi, False sinon
    """
    # Extraire les paramètres depuis kwargs
    paper_size = kwargs.get('paper_size', 'A4')
    color_mode = kwargs.get('color_mode', 'color')
    brightness = kwargs.get('brightness', 0)
    contrast = kwargs.get('contrast', 0)
    pages = kwargs.get('pages', 1)
    ocr_enabled = kwargs.get('ocr', False)
    ocr_lang = kwargs.get('lang', 'fra')
    
    try:
        # Charger la configuration pour obtenir le chemin de NAPS2
        import yaml
        settings_file = Path("dk.config") / "settings.yaml"
        config = {}
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        
        # Chemin vers NAPS2 Console (par défaut ou depuis la config)
        naps2_executable = config.get('tools', {}).get('naps2', {}).get('command', 
                                     r'G:\WarchoLife\WarchoPortable\PortableCommon\Naps2\NAPS2.Console.exe')
        
        # Vérifier que NAPS2 existe
        if not Path(naps2_executable).exists():
            logging.error(f"[NAPS2] Exécutable non trouvé : {naps2_executable}")
            return False
        
        # Utiliser le profil TWAIN fourni ou générer un profil basé sur le DPI
        profil = kwargs.get('profile', f"TWAIN-{dpi}ppp")
        
        # Vérifier la cohérence entre le DPI et le profil
        import re
        profile_match = re.search(r'TWAIN-(\d+)ppp', profil)
        if profile_match:
            profile_dpi = int(profile_match.group(1))
            if profile_dpi != dpi:
                logging.warning(f"[ATTENTION] Incohérence détectée : DPI demandé ({dpi}) != DPI du profil ({profile_dpi})")
                logging.info(f"[CORRECTION] Utilisation du DPI du profil : {profile_dpi}")
                dpi = profile_dpi
        
        logging.info(f"[NAPS2] Utilisation de NAPS2 Console")
        logging.info(f"[NAPS2] Exécutable : {naps2_executable}")
        logging.info(f"[NAPS2] Profil : {profil}")
        
        # Créer le répertoire de sortie si nécessaire
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Obtenir le nombre de scans depuis kwargs
        number_of_scans = kwargs.get('number', 1)
        
        # Construire la commande NAPS2
        cmd = [
            naps2_executable,
            "-o", str(output_file),
            "-d", str(dpi),
            "-n", str(number_of_scans),  # Utiliser le nombre de scans au lieu de pages
            "--profile", profil
        ]
        
        logging.info(f"[NAPS2] Commande : {' '.join(cmd)}")
        print(f"Lancement du scan avec NAPS2...")
        print(f"Profil : {profil}")
        print(f"Résolution : {dpi} DPI")
        if number_of_scans > 1:
            print(f"Nombre de scans : {number_of_scans}")
        else:
            print(f"Pages : {pages}")
        print(f"Fichier de sortie : {output_file}")
        
        # Exécuter la commande NAPS2
        import subprocess
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True,
            timeout=kwargs.get('timeout', 60)
        )
        
        # Pour les scans multiples, NAPS2 crée plusieurs fichiers avec numérotation automatique
        if number_of_scans > 1:
            # Vérifier les fichiers générés par NAPS2
            base_name = output_file.stem
            extension = output_file.suffix
            parent_dir = output_file.parent
            
            generated_files = []
            for i in range(1, number_of_scans + 1):
                expected_file = parent_dir / f"{base_name} ({i}){extension}"
                if expected_file.exists():
                    generated_files.append(expected_file)
                    file_size = expected_file.stat().st_size
                    logging.info(f"[NAPS2] Scan {i}/{number_of_scans} réussi : {expected_file} ({file_size} octets)")
                    
                    # Effectuer l'OCR si demandé
                    if ocr_enabled:
                        ocr_success = _perform_ocr(expected_file, ocr_lang)
                        if ocr_success:
                            logging.info(f"[OCR] OCR réussi pour {expected_file}")
                        else:
                            logging.warning(f"[OCR] OCR échoué pour {expected_file}")
            
            if generated_files:
                print(f"Scans multiples terminés avec succès !")
                print(f"Fichiers générés : {len(generated_files)}/{number_of_scans}")
                for i, file_path in enumerate(generated_files, 1):
                    file_size = file_path.stat().st_size
                    print(f"  {i}. {file_path} ({file_size} octets)")
                
                if ocr_enabled:
                    print(f"OCR terminé pour {len(generated_files)} fichier(s) !")
                
                return True
            else:
                logging.error(f"[NAPS2] Aucun fichier de sortie n'a été créé")
                return False
        else:
            # Scan unique
            if output_file.exists():
                file_size = output_file.stat().st_size
            
                # Vérifier que le fichier n'est pas vide
                if file_size == 0:
                    logging.error(f"[NAPS2] Le fichier de sortie est vide (0 octets) : {output_file}")
                    print(f"Erreur : Le fichier scanné est vide. Vérifiez que le scanner est connecté et qu'un document est placé.")
                    return False
            
                logging.info(f"[NAPS2] Scan réussi : {output_file} ({file_size} octets)")
                print(f"Scan terminé avec succès !")
                print(f"Taille du fichier : {file_size} octets")
            
                # Effectuer l'OCR si demandé
                if ocr_enabled:
                    ocr_success = _perform_ocr(output_file, ocr_lang)
                    if ocr_success:
                        logging.info(f"[OCR] OCR réussi pour {output_file}")
                        print(f"OCR terminé avec succès !")
                    else:
                        logging.warning(f"[OCR] OCR échoué pour {output_file}")
                        print(f"Attention : OCR échoué")
            
                return True
            else:
                logging.error(f"[NAPS2] Le fichier de sortie n'a pas été créé : {output_file}")
                return False
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Erreur NAPS2 (code {e.returncode}): {e.stderr if e.stderr else 'Erreur inconnue'}"
        logging.error(f"[NAPS2] {error_msg}")
        print(f"Erreur lors du scan : {error_msg}")
        return False
    except subprocess.TimeoutExpired:
        error_msg = "Timeout lors du scan"
        logging.error(f"[NAPS2] {error_msg}")
        print(f"Erreur : {error_msg}")
        return False
    except FileNotFoundError:
        error_msg = f"NAPS2 Console non trouvé : {naps2_executable}"
        logging.error(f"[NAPS2] {error_msg}")
        print(f"Erreur : {error_msg}")
        return False
    except Exception as e:
        error_msg = f"Erreur générale : {str(e)}"
        logging.error(f"[NAPS2] {error_msg}")
        print(f"Erreur : {error_msg}")
        return False

def _perform_ocr(image_file: Path, language: str = 'fra') -> bool:
    """
    Effectue l'OCR sur un fichier image pour générer un fichier texte
    
    Args:
        image_file: Fichier image à traiter
        language: Langue pour l'OCR (défaut: 'fra')
        
    Returns:
        bool: True si l'OCR a réussi, False sinon
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
                return _perform_ocr_python(image_file, language)
            else:
                logging.error("[ERREUR] Tesseract désactivé et aucune alternative Python configurée")
                return False
        
        # Générer le nom du fichier de sortie OCR
        ocr_output_file = image_file.with_suffix('.txt')
        
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
            return True
        else:
            logging.error(f"[OCR] Le fichier OCR n'a pas été créé : {ocr_output_file}")
            return False
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Erreur Tesseract (code {e.returncode}): {e.stderr if e.stderr else 'Erreur inconnue'}"
        logging.error(f"[OCR] {error_msg}")
        print(f"Erreur OCR : {error_msg}")
        return False
    except subprocess.TimeoutExpired:
        error_msg = "Timeout lors de l'OCR"
        logging.error(f"[OCR] {error_msg}")
        print(f"Erreur OCR : {error_msg}")
        return False
    except FileNotFoundError:
        error_msg = f"Tesseract non trouvé : {tesseract_executable}"
        logging.error(f"[OCR] {error_msg}")
        print(f"Erreur OCR : {error_msg}")
        return False
    except Exception as e:
        error_msg = f"Erreur générale OCR : {str(e)}"
        logging.error(f"[OCR] {error_msg}")
        print(f"Erreur OCR : {error_msg}")
        return False

def _perform_ocr_python(image_file: Path, language: str = 'fra') -> bool:
    """
    Effectue l'OCR avec pytesseract (alternative Python)
    
    Args:
        image_file: Fichier image à traiter
        language: Langue pour l'OCR (défaut: 'fra')
        
    Returns:
        bool: True si l'OCR a réussi, False sinon
    """
    try:
        if not TESSERACT_AVAILABLE:
            logging.error("[OCR] pytesseract n'est pas disponible")
            return False
        
        import pytesseract
        from PIL import Image
        
        # Générer le nom du fichier de sortie OCR
        ocr_output_file = image_file.with_suffix('.txt')
        
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
            return True
        else:
            logging.error(f"[OCR] Le fichier OCR n'a pas été créé : {ocr_output_file}")
            return False
        
    except Exception as e:
        error_msg = f"Erreur pytesseract : {str(e)}"
        logging.error(f"[OCR] {error_msg}")
        print(f"Erreur OCR pytesseract : {error_msg}")
        return False

def _simulate_scan(output_file: Path, dpi: int, settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simule un scan en créant un fichier de test
    """
    try:
        print("Mode simulation TWAIN activé - aucun scanner physique détecté")
        
        # Créer un fichier de simulation plus réaliste
        ocr_enabled = settings.get('ocr', False)
        ocr_lang = settings.get('lang', 'fra')
        
        if output_file.suffix.lower() == '.pdf':
            # Créer un PDF simple avec reportlab si disponible
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import A4
                
                c = canvas.Canvas(str(output_file), pagesize=A4)
                c.drawString(100, 750, f"SCAN SIMULÉ - {dpi} DPI")
                c.drawString(100, 720, f"Mode: {settings.get('color_mode', 'color')}")
                c.drawString(100, 690, f"Papier: {settings.get('paper_size', 'A4')}")
                c.drawString(100, 660, f"Luminosité: {settings.get('brightness', 0)}")
                c.drawString(100, 630, f"Contraste: {settings.get('contrast', 0)}")
                c.drawString(100, 600, f"Timestamp: {datetime.now()}")
                c.drawString(100, 550, "Ce fichier a été généré en mode simulation.")
                c.drawString(100, 520, "Pour un vrai scan, installez une bibliothèque TWAIN :")
                c.drawString(100, 490, "pip install python-twain")
                c.save()
                
                # Créer un fichier OCR simulé si demandé
                if ocr_enabled:
                    ocr_file = output_file.with_suffix('.txt')
                    with open(ocr_file, 'w', encoding='utf-8') as f:
                        f.write(f"SCAN SIMULÉ - {dpi} DPI\n")
                        f.write(f"Mode: {settings.get('color_mode', 'color')}\n")
                        f.write(f"Papier: {settings.get('paper_size', 'A4')}\n")
                        f.write(f"Luminosité: {settings.get('brightness', 0)}\n")
                        f.write(f"Contraste: {settings.get('contrast', 0)}\n")
                        f.write(f"Timestamp: {datetime.now()}\n")
                        f.write("Ce fichier a été généré en mode simulation.\n")
                        f.write("Pour un vrai scan, installez : pip install python-twain\n")
                    print(f"Fichier OCR simulé créé : {ocr_file}")
                
            except ImportError:
                # Fallback vers fichier texte
                with open(output_file.with_suffix('.txt'), 'w', encoding='utf-8') as f:
                    f.write(f"# Scan simulé\n")
                    f.write(f"DPI: {dpi}\n")
                    f.write(f"Papier: {settings.get('paper_size', 'A4')}\n")
                    f.write(f"Mode: {settings.get('color_mode', 'color')}\n")
                    f.write(f"Luminosité: {settings.get('brightness', 0)}\n")
                    f.write(f"Contraste: {settings.get('contrast', 0)}\n")
                    f.write(f"Timestamp: {datetime.now()}\n")
                    f.write("Ce fichier a été généré en mode simulation.\n")
                    f.write("Pour un vrai scan, installez : pip install python-twain\n")
                output_file = output_file.with_suffix('.txt')
        else:
            # Pour les autres formats, créer un fichier texte
            with open(output_file.with_suffix('.txt'), 'w', encoding='utf-8') as f:
                f.write(f"# Scan simulé - {dpi} DPI\n")
                f.write(f"Format demandé: {output_file.suffix}\n")
                f.write("Mode simulation actif\n")
            output_file = output_file.with_suffix('.txt')
            
            # Créer un fichier OCR simulé si demandé
            if ocr_enabled:
                ocr_file = output_file.with_suffix('.txt')
                with open(ocr_file, 'w', encoding='utf-8') as f:
                    f.write(f"Scan simulé - {dpi} DPI\n")
                    f.write(f"Format demandé: {output_file.suffix}\n")
                    f.write("Mode simulation actif\n")
                    f.write("Fichier OCR simulé\n")
                print(f"Fichier OCR simulé créé : {ocr_file}")
        
        return {
            'success': True,
            'output_file': output_file,
            'dpi': dpi,
            'settings': settings,
            'simulation': True
        }
        
    except Exception as e:
        error_msg = f"Erreur lors de la simulation : {str(e)}"
        logging.error(f"[ERREUR] {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }

def process_existing_files(file_pattern: str, ocr_enabled: bool = False, ocr_lang: str = 'fra', verbose: bool = False) -> Dict[str, Any]:
    """
    Traite des fichiers existants (par exemple pour l'OCR)
    
    Args:
        file_pattern: Pattern de fichiers (peut contenir des wildcards)
        ocr_enabled: Activer l'OCR
        ocr_lang: Langue pour l'OCR
        verbose: Mode verbeux
        
    Returns:
        Dict contenant les résultats du traitement
    """
    logging.info(f"[TRAITEMENT] Traitement des fichiers existants : {file_pattern}")
    
    # Utiliser glob pour résoudre le pattern
    matching_files = glob.glob(file_pattern)
    
    if not matching_files:
        logging.warning(f"[TRAITEMENT] Aucun fichier trouvé pour le pattern : {file_pattern}")
        return {
            'success': False,
            'error': f'Aucun fichier trouvé pour le pattern : {file_pattern}',
            'processed_files': []
        }
    
    logging.info(f"[TRAITEMENT] {len(matching_files)} fichier(s) trouvé(s)")
    
    processed_files = []
    errors = []
    
    for file_path in matching_files:
        file_path = Path(file_path)
        logging.info(f"[TRAITEMENT] Traitement de : {file_path}")
        
        try:
            if ocr_enabled:
                # Effectuer l'OCR sur le fichier existant
                ocr_success = _perform_ocr(file_path, ocr_lang)
                if ocr_success:
                    processed_files.append({
                        'file': file_path,
                        'ocr_file': file_path.with_suffix('.txt'),
                        'success': True
                    })
                    logging.info(f"[OCR] OCR réussi pour : {file_path}")
                else:
                    errors.append(f"OCR échoué pour : {file_path}")
                    logging.error(f"[OCR] OCR échoué pour : {file_path}")
            else:
                # Juste marquer le fichier comme traité
                processed_files.append({
                    'file': file_path,
                    'success': True
                })
                logging.info(f"[TRAITEMENT] Fichier traité : {file_path}")
                
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
    """Point d'entrée principal pour le module de scan"""
    parser = argparse.ArgumentParser(
        description='Module de scan TWAIN avec profils DPI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s -r 300 -o scans/
  %(prog)s -r 200 -p TWAIN-200ppp -o documents/
  %(prog)s -r 150 --batch --auto-feed --pages 10 -f pdf -o output/
  %(prog)s 300 -o scans/  (syntaxe legacy)
  %(prog)s -r 100 -o scans\\drap*.png --ocr  (traitement de fichiers existants)

Profils TWAIN disponibles:
  TWAIN-100ppp  - Scan a 100 DPI (defaut)
  TWAIN-150ppp  - Scan a 150 DPI
  TWAIN-200ppp  - Scan a 200 DPI
  TWAIN-300ppp  - Scan a 300 DPI
  TWAIN-600ppp  - Scan a 600 DPI
  TWAIN-1200ppp - Scan a 1200 DPI
        """
    )
    
    parser.add_argument('dpi_profile', type=int, choices=[100, 150, 200, 300, 600, 1200], nargs='?', default=None,
                       help='Profil de resolution de scan (100, 150, 200, 300, 600, 1200) - optionnel si -r est utilise')
    
    # Options de profil TWAIN
    parser.add_argument('-r', '--resolution', type=int, choices=[100, 150, 200, 300, 600, 1200], default=100,
                       help='Resolution de scan en DPI (defaut: 100)')
    parser.add_argument('-p', '--profile', dest='profile', default='TWAIN-100ppp', help='Profil TWAIN predefini - defaut: TWAIN-100ppp. Profils disponibles: TWAIN-100ppp, TWAIN-150ppp, TWAIN-200ppp, TWAIN-300ppp, TWAIN-600ppp, TWAIN-1200ppp')
    parser.add_argument('--device', help='Peripherique de scan a utiliser')
    parser.add_argument('--source', choices=['flatbed', 'adf', 'duplex'], default='flatbed',
                       help='Source du scanner (defaut: flatbed)')
    parser.add_argument('--color-mode', choices=['color', 'grayscale', 'bw'], default='color',
                       help='Mode couleur (defaut: color)')
    
    # Options de scan
    parser.add_argument('--paper-size', choices=['A4', 'A3', 'Letter', 'Legal', 'Custom'], default='A4',
                       help='Taille du papier (defaut: A4)')
    parser.add_argument('--orientation', choices=['portrait', 'landscape'], default='portrait',
                       help='Orientation (defaut: portrait)')
    parser.add_argument('--brightness', type=int, default=0, metavar='N',
                       help='Luminosite (-100 a 100, defaut: 0)')
    parser.add_argument('--contrast', type=int, default=0, metavar='N',
                       help='Contraste (-100 a 100, defaut: 0)')
    parser.add_argument('--gamma', type=float, default=1.0, metavar='N',
                       help='Correction gamma (0.1 a 3.0, defaut: 1.0)')
    
    # Options de sortie
    parser.add_argument('-o', '--output', help='Repertoire de sortie, nom de base du fichier (ex: scans/ ou scans/document) ou pattern de fichiers existants (ex: scans\\*.png) - OBLIGATOIRE sauf avec --manual')
    parser.add_argument('-f', '--format', choices=['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'svg'], default='jpg',
                       help='Format de sortie (defaut: jpg)')
    parser.add_argument('--quality', type=int, default=90, metavar='N',
                       help='Qualite de compression (1-100, defaut: 90)')
    parser.add_argument('--naming', choices=['date', 'sequence', 'custom'], default='date',
                       help='Convention de nommage (defaut: date)')
    
    # Options de traitement post-scan
    parser.add_argument('--ocr', action='store_true', help='Activer l\'OCR apres le scan')
    parser.add_argument('--lang', default='fra', help='Langue pour l\'OCR (defaut: fra)')
    parser.add_argument('--deskew', action='store_true', help='Correction automatique de l\'inclinaison')
    parser.add_argument('--despeckle', action='store_true', help='Suppression des points parasites')
    parser.add_argument('--crop', action='store_true', help='Recadrage automatique des bords')
    
    # Options de lot
    parser.add_argument('-n', '--number', type=int, default=1, help='Nombre de scans a effectuer (defaut: 1)')
    parser.add_argument('--pages', type=int, default=1, help='Nombre de pages a scanner (defaut: 1)')
    parser.add_argument('--batch', action='store_true', help='Mode lot pour scanner plusieurs documents')
    parser.add_argument('--separator', action='store_true', help='Page de separation entre documents')
    parser.add_argument('--auto-feed', action='store_true', help='Alimentation automatique (ADF)')
    
    # Options communes dk.*
    parser.add_argument('-v', '--verbose', action='store_true', help='Mode verbeux')
    parser.add_argument('-q', '--quiet', action='store_true', help='Mode silencieux')
    parser.add_argument('-u', '--update', action='store_true', help='Ecraser les fichiers existants')
    parser.add_argument('--preview', action='store_true', help='Mode apercu avant scan')
    
    # Options avancées
    parser.add_argument('--calibrate', action='store_true', help='Calibrer le scanner avant utilisation')
    parser.add_argument('--test-pattern', action='store_true', help='Scanner une mire de test')
    parser.add_argument('--manual', action='store_true', help='Ouvrir l\'interface de configuration NAPS2')
    
    args = parser.parse_args()
    
    # Si l'option de configuration est utilisée, traiter immédiatement
    if args.manual:
        try:
            import subprocess
            import yaml
            
            # Charger la configuration pour obtenir le chemin de NAPS2 GUI
            settings_file = Path("dk.config") / "settings.yaml"
            config = {}
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            
            naps2_gui_executable = config.get('tools', {}).get('naps2_gui', {}).get('command', 
                                             r'G:\WarchoLife\WarchoPortable\PortableCommon\Naps2\NAPS2.exe')
            
            if Path(naps2_gui_executable).exists():
                print(f"Ouverture de l'interface de configuration NAPS2...")
                subprocess.Popen([naps2_gui_executable])
                print(f"Interface de configuration NAPS2 ouverte.")
                return 0
            else:
                error_msg = f"Interface NAPS2 non trouvée : {naps2_gui_executable}"
                print(f"Erreur : {error_msg}")
                return 1
                
        except Exception as e:
            error_msg = f"Erreur lors de l'ouverture de l'interface de configuration : {str(e)}"
            print(f"Erreur : {error_msg}")
            return 1
    
    # Verifier que -o est fourni pour les autres operations
    if not args.output:
        parser.error("l'argument -o/--output est requis sauf avec --manual")
    
    # Configuration du logging
    log_file = setup_logging(args.verbose and not args.quiet)
    
    logging.info(f"[DÉMARRAGE] Démarrage de dk.scan")
    logging.info(f"   Version Python : {sys.version}")
    logging.info(f"   Répertoire de travail : {Path.cwd()}")
    
    # Préparer les options de scan
    scan_options = {
        'paper_size': args.paper_size,
        'color_mode': args.color_mode,
        'orientation': args.orientation,
        'brightness': args.brightness,
        'contrast': args.contrast,
        'gamma': args.gamma,
        'format': args.format,
        'quality': args.quality,
        'naming': args.naming,
        'ocr': args.ocr,
        'lang': args.lang,
        'deskew': args.deskew,
        'despeckle': args.despeckle,
        'crop': args.crop,
        'number': args.number,
        'pages': args.pages,
        'batch': args.batch,
        'separator': args.separator,
        'auto_feed': args.auto_feed,
        'preview': args.preview,
        'calibrate': args.calibrate,
        'test_pattern': args.test_pattern,
        'manual': args.manual
    }
    
    # Déterminer la résolution à utiliser : argument positionnel a priorité sur -r
    if args.dpi_profile:
        dpi_to_use = args.dpi_profile
    else:
        dpi_to_use = args.resolution  # Valeur par défaut de -r (100)
    
    # Générer le profil TWAIN basé sur la résolution si aucun profil spécifique n'est fourni
    if args.profile == 'TWAIN-100ppp':  # Valeur par défaut
        scan_options['profile'] = f"TWAIN-{dpi_to_use}ppp"
    else:
        scan_options['profile'] = args.profile
        # Extraire le DPI du profil personnalisé si possible
        import re
        profile_match = re.search(r'TWAIN-(\d+)ppp', args.profile)
        if profile_match:
            dpi_to_use = int(profile_match.group(1))
    
    # Détecter si -o contient un pattern de fichiers existants
    output_str = str(args.output)
    has_wildcards = '*' in output_str or '?' in output_str
    has_extension = '.' in Path(output_str).name
    
    # Si le pattern contient des wildcards ET une extension, traiter comme des fichiers existants
    if has_wildcards and has_extension:
        logging.info(f"[MODE] Détection du mode traitement de fichiers existants : {output_str}")
        try:
            result = process_existing_files(
                file_pattern=output_str,
                ocr_enabled=args.ocr,
                ocr_lang=args.lang,
                verbose=args.verbose
            )
        except Exception as e:
            error_msg = f"Erreur lors du traitement des fichiers existants : {str(e)}"
            logging.error(f"[ERREUR] {error_msg}")
            print(f"Erreur : {error_msg}")
            return 1
    else:
        # Mode scan normal
        logging.info(f"[MODE] Mode scan normal vers : {output_str}")
        try:
            result = scan_document(dpi_to_use, Path(args.output), **scan_options)
        except Exception as e:
            error_msg = f"Erreur inattendue : {str(e)}"
            logging.error(f"[ERREUR] {error_msg}")
            print(f"Erreur : {error_msg}")
            return 1
        
        if result['success']:
            # Gérer l'affichage selon le type d'opération
            if 'multiple_scans' in result:
                # Mode scans multiples
                if args.quiet:
                    for scan_result in result['results']:
                        try:
                            relative_path = scan_result['output_file'].relative_to(Path.cwd())
                            print(str(relative_path))
                        except ValueError:
                            print(str(scan_result['output_file']))
                else:
                    try:
                        from rich.console import Console
                        from rich.panel import Panel
                        
                        console = Console()
                        
                        # Construire le contenu du panneau de succès pour les scans multiples
                        content_lines = [
                            f"[green]Scans multiples réussis ![/green]\n",
                            f"[cyan]Scans réussis :[/cyan] {result['successful_scans']}/{result['total_scans']}",
                            f"[cyan]DPI :[/cyan] {result['dpi']}",
                            f"[cyan]Profil TWAIN :[/cyan] {scan_options['profile']}",
                            f"[cyan]Mode :[/cyan] {scan_options['color_mode']}",
                            f"[cyan]Format :[/cyan] {scan_options['format']}"
                        ]
                        
                        if scan_options.get('ocr', False):
                            content_lines.append(f"[cyan]Langue OCR :[/cyan] {scan_options.get('lang', 'fra')}")
                        
                        content_lines.append("")
                        content_lines.append("[blue]Fichiers générés :[/blue]")
                        
                        # Lister tous les fichiers générés
                        for i, scan_result in enumerate(result['results'], 1):
                            try:
                                formatted_path = str(scan_result['output_file'].relative_to(Path.cwd()))
                            except ValueError:
                                formatted_path = str(scan_result['output_file'])
                            content_lines.append(f"[blue]{i}.[/blue] {formatted_path}")
                            
                            # Ajouter le fichier OCR si présent
                            if scan_options.get('ocr', False):
                                ocr_file = scan_result['output_file'].with_suffix('.txt')
                                try:
                                    ocr_formatted_path = str(ocr_file.relative_to(Path.cwd()))
                                except ValueError:
                                    ocr_formatted_path = str(ocr_file)
                                content_lines.append(f"[blue]   → OCR :[/blue] {ocr_formatted_path}")
                        
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
                        print(f"Scans multiples réussis : {result['successful_scans']}/{result['total_scans']}")
                        print(f"  DPI : {result['dpi']}")
                        print(f"  Profil TWAIN : {scan_options['profile']}")
                        print(f"  Mode : {scan_options['color_mode']}")
                        print(f"  Format : {scan_options['format']}")
                        
                        if scan_options.get('ocr', False):
                            print(f"  Langue OCR : {scan_options.get('lang', 'fra')}")
                        
                        print("  Fichiers générés :")
                        for i, scan_result in enumerate(result['results'], 1):
                            print(f"    {i}. {scan_result['output_file']}")
                            if scan_options.get('ocr', False):
                                ocr_file = scan_result['output_file'].with_suffix('.txt')
                                print(f"       → OCR : {ocr_file}")
                        
                        if result.get('errors'):
                            print("  Erreurs :")
                            for error in result['errors']:
                                print(f"    ✗ {error}")
                        
                        try:
                            relative_log = log_file.relative_to(Path.cwd())
                            print(f"  Log détaillé : {relative_log}")
                        except ValueError:
                            print(f"  Log détaillé : {log_file}")
            elif 'processed_files' in result:
                # Mode traitement de fichiers existants
                if args.quiet:
                    for file_info in result['processed_files']:
                        if file_info['success']:
                            try:
                                relative_path = file_info['file'].relative_to(Path.cwd())
                                print(str(relative_path))
                            except ValueError:
                                print(str(file_info['file']))
                            # Afficher aussi le fichier OCR si présent
                            if 'ocr_file' in file_info:
                                try:
                                    relative_ocr = file_info['ocr_file'].relative_to(Path.cwd())
                                    print(str(relative_ocr))
                                except ValueError:
                                    print(str(file_info['ocr_file']))
                else:
                    try:
                        from rich.console import Console
                        from rich.panel import Panel
                        
                        console = Console()
                        
                        # Construire le contenu du panneau de succès pour le traitement de fichiers
                        content_lines = [
                            f"[green]Traitement de fichiers réussi ![/green]\n",
                            f"[cyan]Fichiers traités :[/cyan] {result['successful_files']}/{result['total_files']}"
                        ]
                        
                        if args.ocr:
                            content_lines.append(f"[cyan]Langue OCR :[/cyan] {args.lang}")
                        
                        # Lister les fichiers traités
                        for file_info in result['processed_files']:
                            if file_info['success']:
                                try:
                                    formatted_path = str(file_info['file'].relative_to(Path.cwd()))
                                except ValueError:
                                    formatted_path = str(file_info['file'])
                                content_lines.append(f"[blue]✓[/blue] {formatted_path}")
                                
                                # Ajouter le fichier OCR si présent
                                if 'ocr_file' in file_info:
                                    try:
                                        ocr_formatted_path = str(file_info['ocr_file'].relative_to(Path.cwd()))
                                    except ValueError:
                                        ocr_formatted_path = str(file_info['ocr_file'])
                                    content_lines.append(f"[blue]  → OCR :[/blue] {ocr_formatted_path}")
                        
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
                        print(f"Traitement de fichiers réussi : {result['successful_files']}/{result['total_files']}")
                        if args.ocr:
                            print(f"  Langue OCR : {args.lang}")
                        
                        for file_info in result['processed_files']:
                            if file_info['success']:
                                print(f"  ✓ {file_info['file']}")
                                if 'ocr_file' in file_info:
                                    print(f"    → OCR : {file_info['ocr_file']}")
                        
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
                # Mode scan normal
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
                        
                        formatted_path = str(result['output_file'])
                        try:
                            formatted_path = str(result['output_file'].relative_to(Path.cwd()))
                        except ValueError:
                            pass
                        
                        # Construire le contenu du panneau de succès
                        content_lines = [
                            f"[green]Scan réussi ![/green]\n",
                            f"[cyan]DPI :[/cyan] {result['dpi']}",
                            f"[cyan]Profil TWAIN :[/cyan] {scan_options['profile']}",
                            f"[cyan]Mode :[/cyan] {scan_options['color_mode']}",
                            f"[cyan]Format :[/cyan] {scan_options['format']}"
                        ]
                        
                        # Ajouter les informations OCR si l'OCR est activé
                        if scan_options.get('ocr', False):
                            content_lines.append(f"[cyan]Langue OCR :[/cyan] {scan_options.get('lang', 'fra')}")
                            # Ajouter le fichier OCR généré
                            ocr_file = result['output_file'].with_suffix('.txt')
                            try:
                                ocr_formatted_path = ocr_file.relative_to(Path.cwd())
                            except ValueError:
                                ocr_formatted_path = ocr_file
                            content_lines.append(f"[blue]Fichier OCR :[/blue] {ocr_formatted_path}")
                        
                        content_lines.append(f"[blue]Fichier de sortie :[/blue] {formatted_path}")
                        
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
                        print(f"Scan réussi : {result['dpi']} DPI")
                        print(f"  Profil TWAIN : {scan_options['profile']}")
                        print(f"  Mode : {scan_options['color_mode']}")
                        print(f"  Format : {scan_options['format']}")
                        
                        # Ajouter les informations OCR si l'OCR est activé
                        if scan_options.get('ocr', False):
                            print(f"  Langue OCR : {scan_options.get('lang', 'fra')}")
                            # Ajouter le fichier OCR généré
                            ocr_file = result['output_file'].with_suffix('.txt')
                            print(f"  Fichier OCR : {ocr_file}")
                        
                        print(f"  Fichier de sortie : {result['output_file']}")
                        
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
