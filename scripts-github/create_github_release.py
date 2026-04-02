#!/usr/bin/env python3
"""
Script pour créer une release GitHub avec upload de la wheel.

Usage:
    1. Définir la variable d'environnement GITHUB_TOKEN
    2. Exécuter: python create_github_release.py

Ou:
    python create_github_release.py --token YOUR_GITHUB_TOKEN
"""

import os
import sys
import json
import requests
from pathlib import Path
import argparse


def create_github_release(token: str, version: str, wheel_path: Path):
    """
    Crée une release GitHub et uploade la wheel.

    Args:
        token: Token GitHub avec permissions repo
        version: Version de la release (ex: "3.4.0")
        wheel_path: Chemin vers le fichier wheel
    """
    repo_owner = "warchosian"
    repo_name = "ambulon"

    # Vérifier que la wheel existe
    if not wheel_path.exists():
        print(f"❌ Erreur : Wheel introuvable à {wheel_path}")
        return False

    print(f"📦 Wheel trouvée : {wheel_path.name} ({wheel_path.stat().st_size / 1024:.1f} KB)")

    # Préparer les données de la release
    release_data = {
        "tag_name": version,
        "name": f"v{version} - Pipeline RAG complet avec publication automatique",
        "body": """## 🎯 Nouvelles fonctionnalités majeures

### Pipeline RAG complet (5 étapes)
- ✅ Gestion interactive des contraintes réseau VPN
- ✅ Détection localisation (intranet/externe)
- ✅ Vérifications réseau avant chaque étape VPN
- ✅ **Étape 5 : Publication automatique HTML interactif + PDF**
- ✅ Organisation des documents dans `workplace-ambulon/doc-kit/`

### Documentation
- ✅ Amélioration `doc/sireines.automation.md`
- ✅ Annotations VPN (🔒) sur toutes les phases
- ✅ Clarification organisation automatique

### Installation
```bash
pip install ambulon-{version}-py3-none-any.whl
```
""".replace("{version}", version),
        "draft": False,
        "prerelease": False
    }

    # Headers pour l'API GitHub
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }

    # 1. Créer la release
    print(f"\n🚀 Création de la release {version}...")
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases"

    try:
        response = requests.post(api_url, headers=headers, json=release_data)
        response.raise_for_status()
        release = response.json()

        print(f"✅ Release créée : {release['html_url']}")

        # 2. Uploader la wheel
        print(f"\n📤 Upload de la wheel...")
        upload_url = release['upload_url'].replace('{?name,label}', '')
        upload_url = f"{upload_url}?name={wheel_path.name}"

        upload_headers = {
            "Authorization": f"token {token}",
            "Content-Type": "application/octet-stream"
        }

        with open(wheel_path, 'rb') as f:
            upload_response = requests.post(upload_url, headers=upload_headers, data=f)
            upload_response.raise_for_status()

        print(f"✅ Wheel uploadée avec succès !")
        print(f"\n🎉 Release complète disponible : {release['html_url']}")

        return True

    except requests.exceptions.HTTPError as e:
        print(f"❌ Erreur HTTP : {e}")
        print(f"Réponse : {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False


def mask_token(token: str) -> str:
    """
    Masque le token en affichant seulement le début et la fin.

    Args:
        token: Token à masquer

    Returns:
        Token masqué (ex: "ghp_abc...xyz")
    """
    if len(token) <= 8:
        return "***"
    return f"{token[:8]}...{token[-4:]}"


def main():
    parser = argparse.ArgumentParser(description="Créer une release GitHub avec la wheel")
    parser.add_argument('--token', help='GitHub token (ou via GITHUB_TOKEN env var)')
    parser.add_argument('--version', default='3.4.0', help='Version à publier (défaut: 3.4.0)')
    parser.add_argument('--wheel', help='Chemin vers la wheel (défaut: dist/ambulon-{version}-py3-none-any.whl)')

    args = parser.parse_args()

    # Récupérer le token
    token = args.token or os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ Erreur : Token GitHub requis")
        print("\nDéfinir via :")
        print("  - Variable d'environnement: export GITHUB_TOKEN=your_token")
        print("  - Argument: --token your_token")
        sys.exit(1)

    # Afficher le token masqué pour vérification
    print(f"🔑 Token GitHub détecté : {mask_token(token)}")
    print(f"   Longueur : {len(token)} caractères")

    # Chemin de la wheel
    wheel_path = Path(args.wheel) if args.wheel else Path(f"dist/ambulon-{args.version}-py3-none-any.whl")

    # Créer la release
    success = create_github_release(token, args.version, wheel_path)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
