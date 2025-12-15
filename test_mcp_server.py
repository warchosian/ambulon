#!/usr/bin/env python3
"""Script de test pour le serveur MCP Ambulon."""

import asyncio
import json
import sys
from pathlib import Path

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ambulon.mcp import handle_list_tools, handle_call_tool


async def test_list_tools():
    """Test de la liste des outils."""
    print("=== Test de la liste des outils ===")
    try:
        tools = await handle_list_tools()
        print(f"OK {len(tools)} outils disponibles:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        return True
    except Exception as e:
        print(f"ERREUR: {e}")
        return False


async def test_scan_tool():
    """Test de l'outil de scan."""
    print("\n=== Test de l'outil de scan ===")
    try:
        arguments = {
            "dpi": 300,
            "output_path": "test_scans/test_scan.jpg",
            "format": "jpg",
            "paper_size": "A4"
        }
        
        result = await handle_call_tool("scan_document", arguments)
        print(f"OK Outil de scan teste avec succes")
        print(f"  Résultat: {result.content[0].text[:100]}...")
        return True
    except Exception as e:
        print(f"ERREUR: {e}")
        return False


async def test_ocr_tool():
    """Test de l'outil OCR."""
    print("\n=== Test de l'outil OCR ===")
    try:
        # Créer un fichier image factice pour le test
        test_image = Path("test_image.jpg")
        test_image.write_bytes(b"fake image data for testing")
        
        arguments = {
            "image_path": str(test_image),
            "language": "fra"
        }
        
        result = await handle_call_tool("ocr_image", arguments)
        print(f"OK Outil OCR teste")
        print(f"  Résultat: {result.content[0].text[:100]}...")
        
        # Nettoyer
        if test_image.exists():
            test_image.unlink()
        
        return True
    except Exception as e:
        print(f"ERREUR: {e}")
        # Nettoyer en cas d'erreur
        test_image = Path("test_image.jpg")
        if test_image.exists():
            test_image.unlink()
        return False


async def test_batch_ocr_tool():
    """Test de l'outil OCR en lot."""
    print("\n=== Test de l'outil OCR en lot ===")
    try:
        arguments = {
            "pattern": "scans/*.jpg",
            "language": "fra",
            "output_dir": "textes/"
        }
        
        result = await handle_call_tool("ocr_batch", arguments)
        print(f"OK Outil OCR en lot teste")
        print(f"  Résultat: {result.content[0].text[:100]}...")
        return True
    except Exception as e:
        print(f"ERREUR: {e}")
        return False


async def test_scan_with_ocr_tool():
    """Test de l'outil scan + OCR."""
    print("\n=== Test de l'outil scan + OCR ===")
    try:
        arguments = {
            "dpi": 300,
            "output_path": "test_scans/scan_with_ocr.jpg",
            "ocr_lang": "fra"
        }
        
        result = await handle_call_tool("scan_with_ocr", arguments)
        print(f"OK Outil scan + OCR teste")
        print(f"  Résultat: {result.content[0].text[:100]}...")
        return True
    except Exception as e:
        print(f"ERREUR: {e}")
        return False


async def main():
    """Fonction principale de test."""
    print("Test du serveur MCP Ambulon")
    print("=" * 50)
    
    tests = [
        ("Liste des outils", test_list_tools),
        ("Outil de scan", test_scan_tool),
        ("Outil OCR", test_ocr_tool),
        ("Outil OCR en lot", test_batch_ocr_tool),
        ("Outil scan + OCR", test_scan_with_ocr_tool),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            if success:
                passed += 1
        except Exception as e:
            print(f"ERREUR {test_name}: Exception non geree - {e}")
    
    print(f"\n{'=' * 50}")
    print(f"Resultats: {passed}/{total} tests reussis")
    
    if passed == total:
        print("Tous les tests sont passes ! Le serveur MCP fonctionne parfaitement.")
        return 0
    else:
        print("ATTENTION: Certains tests ont echoue. Verifiez la configuration.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
