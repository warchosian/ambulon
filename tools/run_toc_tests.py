#!/usr/bin/env python
"""
Script pour lancer les tests unitaires du module TOC
"""

import sys
import os
import subprocess
from pathlib import Path


def main():
    """Lancer les tests TOC"""
    # Se placer dans le répertoire du projet
    script_dir = Path(__file__).parent.parent.resolve()
    os.chdir(script_dir)
    
    # Ajouter src au PYTHONPATH
    env = os.environ.copy()
    env['PYTHONPATH'] = str(script_dir / 'src')
    
    print("=" * 60)
    print("Tests unitaires du module TOC")
    print("=" * 60)
    print()
    
    # Nettoyer le cache
    print("[1/4] Nettoyage du cache...")
    cache_script = script_dir / 'tools' / 'clear_pycache.py'
    if cache_script.exists():
        subprocess.run([sys.executable, str(cache_script)], 
                      capture_output=True, check=False)
    print()
    
    # Vérifier pytest
    print("[2/4] Vérification de pytest...")
    result = subprocess.run([sys.executable, '-c', 'import pytest'],
                          capture_output=True, check=False)
    if result.returncode != 0:
        print("ERREUR: pytest n'est pas installé")
        print("Installation: pip install pytest pytest-cov")
        return 1
    print("OK")
    print()
    
    # Lancer les tests
    print("[3/4] Exécution des tests...")
    print()
    
    test_dir = script_dir / 'tests' / 'unit' / 'toc'
    if not test_dir.exists():
        print(f"ERREUR: Répertoire de tests non trouvé: {test_dir}")
        return 1
    
    # Commande pytest
    cmd = [
        sys.executable, '-m', 'pytest',
        str(test_dir),
        '-v',
        '--tb=short',
        '-x'  # Arrêter au premier échec
    ]
    
    # Ajouter --color si sur terminal
    if sys.stdout.isatty():
        cmd.append('--color=yes')
    
    result = subprocess.run(cmd, env=env)
    
    if result.returncode != 0:
        print()
        print("=" * 60)
        print("ERREUR: Des tests ont échoué")
        print("=" * 60)
        return 1
    
    print()
    print("=" * 60)
    print("SUCCÈS: Tous les tests sont passés!")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
