"""
Exemple d'utilisation de l'API Alibaba Cloud (Qwen) avec Ambulon.

Ce fichier démontre comment utiliser correctement les clés API
depuis les variables d'environnement.
"""

import os
import sys
from pathlib import Path

# Charger les variables d'environnement depuis .env (optionnel, automatique si config existe)
try:
    from dotenv import load_dotenv
    load_dotenv()  # Charge .env si python-dotenv est installé
except ImportError:
    pass  # python-dotenv pas installé, utiliser les variables d'env système


def get_alibaba_client():
    """
    Crée un client Alibaba Cloud en utilisant la clé API depuis .env.

    Returns:
        Client Alibaba configuré

    Raises:
        ValueError: Si la clé API n'est pas définie
    """
    api_key = os.getenv("ALIBABA_API_KEY")

    if not api_key:
        raise ValueError(
            "ALIBABA_API_KEY non définie. "
            "Veuillez la configurer dans .env ou en variable d'environnement."
        )

    # Exemple avec un client OpenAI-compatible
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        return client
    except ImportError:
        print("Erreur: Installer openai avec: pip install openai", file=sys.stderr)
        sys.exit(1)


def test_alibaba_api():
    """Test basique de l'API Alibaba Cloud."""
    print("🔧 Test de l'API Alibaba Cloud (Qwen)...")

    try:
        client = get_alibaba_client()

        # Test avec un prompt simple
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "user", "content": "Bonjour ! Réponds en une phrase."}
            ],
            max_tokens=50
        )

        answer = response.choices[0].message.content
        print(f"✅ API Alibaba fonctionne !")
        print(f"📝 Réponse : {answer}")

        return True

    except Exception as e:
        print(f"❌ Erreur lors du test de l'API : {e}", file=sys.stderr)
        return False


def main():
    """Point d'entrée de l'exemple."""
    # Vérifier que la clé est configurée
    api_key = os.getenv("ALIBABA_API_KEY")

    if not api_key:
        print("❌ ALIBABA_API_KEY non définie !", file=sys.stderr)
        print("\nConfiguration requise :", file=sys.stderr)
        print("1. Créer un fichier .env à la racine du projet", file=sys.stderr)
        print("2. Ajouter : ALIBABA_API_KEY=sk-xxx", file=sys.stderr)
        print("3. OU définir la variable d'environnement système", file=sys.stderr)
        return 1

    # Masquer la clé pour l'affichage
    masked_key = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 14 else "***"
    print(f"✅ ALIBABA_API_KEY configurée : {masked_key}")

    # Tester l'API
    success = test_alibaba_api()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
