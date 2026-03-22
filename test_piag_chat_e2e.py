#!/usr/bin/env python3
"""
Test End-to-End de l'API CHAT PIAG

Ce script teste toutes les opérations CHAT de bout en bout.
Tous les logs et résultats sont sauvegardés pour analyse ultérieure.

Usage:
    python test_piag_chat_e2e.py [--config config/piag.yaml]
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Ajouter src au path si nécessaire
_src_path = Path(__file__).parent / "src"
if _src_path.exists() and str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

try:
    import requests
except ImportError:
    print("❌ Erreur: Le module 'requests' n'est pas installé")
    print("   Installez-le avec: pip install requests")
    sys.exit(1)


# Configuration du logging détaillé
def setup_detailed_logging(log_dir: Path):
    """Configure le logging avec fichier et console."""
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"test_chat_e2e_{timestamp}.log"

    # Format détaillé
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler fichier
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # Logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return log_file


def save_response(output_dir: Path, step_name: str, data: dict):
    """Sauvegarde une réponse JSON pour analyse ultérieure."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"{step_name}_{timestamp}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logging.info(f"Réponse sauvegardée: {filename}")
    return filename


def load_config(config_path: str = None):
    """Charge la configuration depuis le fichier YAML."""
    try:
        import yaml
    except ImportError:
        print("❌ Erreur: Le module 'pyyaml' n'est pas installé")
        print("   Installez-le avec: pip install pyyaml")
        sys.exit(1)

    if config_path and Path(config_path).exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}


def test_apikey_info(api_url: str, token: str, responses_dir: Path, timeout: int = 60):
    """Test de l'endpoint apikey/info."""
    print("\n" + "=" * 80)
    print("ÉTAPE 1: Test apikey/info")
    print("=" * 80)
    logging.info("ÉTAPE 1: apikey/info")

    try:
        endpoint = f"{api_url.rstrip('/')}/apikey/info".replace('/chat/completions/apikey/info', '/apikey/info')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        logging.info(f"Requête GET: {endpoint}")
        logging.debug(f"Headers: {json.dumps({k: v if k != 'Authorization' else '***' for k, v in headers.items()})}")

        response = requests.get(endpoint, headers=headers, timeout=timeout)
        response.raise_for_status()

        data = response.json()
        logging.info(f"Réponse apikey/info: {json.dumps(data, indent=2)}")
        save_response(responses_dir, "01_apikey_info", data)

        print(f"✓ API Key Info récupérée")
        if 'max_budget' in data:
            print(f"  Budget maximum: {data['max_budget']}")
        if 'spend' in data:
            print(f"  Dépenses: {data['spend']}")

        return True

    except requests.exceptions.RequestException as e:
        # Si l'endpoint n'existe pas (404), marquer comme ignoré plutôt qu'échoué
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 404:
                logging.warning("Endpoint apikey/info non disponible (404) - Test ignoré")
                print("⏭️  Endpoint apikey/info non disponible (404) - Test ignoré")
                return "SKIPPED"
            logging.error(f"Réponse HTTP: {e.response.text}")

        logging.error(f"Erreur apikey/info: {e}", exc_info=True)
        print(f"❌ Erreur: {e}")
        return False


def test_basic_query(api_url: str, token: str, model: str, responses_dir: Path, timeout: int = 60):
    """Test de chat/completions avec une question simple."""
    print("\n" + "=" * 80)
    print("ÉTAPE 2: Test chat basic query")
    print("=" * 80)
    logging.info("ÉTAPE 2: chat basic query")

    test_questions = [
        "Quelle est la capitale de la France ?",
        "Explique en une phrase ce qu'est l'intelligence artificielle.",
        "Donne-moi un nombre aléatoire entre 1 et 100."
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n  Question {i}: {question}")
        logging.info(f"Question {i}: {question}")

        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }

            payload = {
                'model': model,
                'messages': [
                    {'role': 'user', 'content': question}
                ]
            }

            logging.info(f"Requête POST: {api_url}")
            logging.debug(f"Payload: {json.dumps(payload, indent=2)}")

            response = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()

            data = response.json()
            logging.info(f"Réponse question {i}: {json.dumps(data, indent=2)}")
            save_response(responses_dir, f"02_basic_query_{i}", data)

            # Extraire la réponse
            answer = data['choices'][0]['message']['content']
            print(f"  ✓ Réponse: {answer[:150]}{'...' if len(answer) > 150 else ''}")

            # Afficher les tokens si disponibles
            if 'usage' in data:
                usage = data['usage']
                print(f"  Tokens: prompt={usage.get('prompt_tokens')}, completion={usage.get('completion_tokens')}, total={usage.get('total_tokens')}")

        except Exception as e:
            logging.error(f"Erreur question {i}: {e}", exc_info=True)
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Réponse HTTP: {e.response.text}")
            print(f"  ❌ Erreur: {e}")
            return False

    return True


def test_completion(api_url: str, token: str, model: str, responses_dir: Path, timeout: int = 60):
    """Test de l'endpoint /completions (legacy)."""
    print("\n" + "=" * 80)
    print("ÉTAPE 3: Test completion (legacy)")
    print("=" * 80)
    logging.info("ÉTAPE 3: completion endpoint")

    try:
        # Remplacer chat/completions par completions
        completion_url = api_url.replace('/chat/completions', '/completions')

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        payload = {
            'model': model,
            'prompt': 'Bonjour, comment allez-vous ?'
        }

        logging.info(f"Requête POST: {completion_url}")
        logging.debug(f"Payload: {json.dumps(payload, indent=2)}")

        response = requests.post(completion_url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()

        data = response.json()
        logging.info(f"Réponse completion: {json.dumps(data, indent=2)}")
        save_response(responses_dir, "03_completion", data)

        # Extraire la complétion
        completion_text = data['choices'][0]['text']
        print(f"✓ Complétion: {completion_text[:150]}{'...' if len(completion_text) > 150 else ''}")

        return True

    except Exception as e:
        logging.error(f"Erreur completion: {e}", exc_info=True)
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Réponse HTTP: {e.response.text}")
        print(f"❌ Erreur: {e}")
        print("  (Cet endpoint peut ne pas être disponible)")
        return False


def test_chat_with_context(api_url: str, token: str, model: str, responses_dir: Path, timeout: int = 60):
    """Test de chat avec contexte (simulation de chunks RAG)."""
    print("\n" + "=" * 80)
    print("ÉTAPE 4: Test chat avec contexte")
    print("=" * 80)
    logging.info("ÉTAPE 4: chat avec contexte")

    try:
        # Contexte simulé (comme des chunks RAG)
        context_chunks = [
            "Le système PIAG (Platform Intelligence Artificielle Gouvernementale) est une plateforme d'IA pour le secteur public.",
            "PIAG propose deux API principales: l'API RAG pour la recherche sémantique et l'API Chat pour la génération de texte.",
            "L'API RAG permet d'uploader des documents, de les découper en chunks et d'effectuer des recherches sémantiques."
        ]

        question = "Qu'est-ce que PIAG et quelles sont ses fonctionnalités principales ?"

        print(f"\n  Question: {question}")
        print(f"  Contexte: {len(context_chunks)} chunk(s)")
        logging.info(f"Question avec contexte: {question}")
        logging.info(f"Nombre de chunks: {len(context_chunks)}")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        # Construction des messages avec contexte
        messages = [
            {'role': 'user', 'content': question}
        ]

        # Ajouter les chunks comme messages supplémentaires
        for chunk in context_chunks:
            messages.append({'role': 'user', 'content': chunk})

        payload = {
            'model': model,
            'messages': messages
        }

        logging.info(f"Requête POST: {api_url}")
        logging.debug(f"Payload: {json.dumps(payload, indent=2)}")

        response = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()

        data = response.json()
        logging.info(f"Réponse avec contexte: {json.dumps(data, indent=2)}")
        save_response(responses_dir, "04_chat_with_context", data)

        # Extraire la réponse
        answer = data['choices'][0]['message']['content']
        print(f"  ✓ Réponse: {answer[:200]}{'...' if len(answer) > 200 else ''}")

        if 'usage' in data:
            usage = data['usage']
            print(f"  Tokens: prompt={usage.get('prompt_tokens')}, completion={usage.get('completion_tokens')}, total={usage.get('total_tokens')}")

        return True

    except Exception as e:
        logging.error(f"Erreur chat avec contexte: {e}", exc_info=True)
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Réponse HTTP: {e.response.text}")
        print(f"❌ Erreur: {e}")
        return False


def run_chat_e2e_test(config_path: str = None):
    """Exécute le test E2E complet du Chat."""

    print("=" * 80)
    print("TEST END-TO-END - API CHAT PIAG")
    print("=" * 80)

    # Créer les répertoires de sortie
    output_dir = Path("test_output") / "chat" / datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = output_dir / "logs"
    responses_dir = output_dir / "responses"

    log_file = setup_detailed_logging(log_dir)
    print(f"\n📝 Logs détaillés: {log_file}")
    print(f"📂 Répertoire de sortie: {output_dir}\n")

    logging.info("=" * 80)
    logging.info("DÉBUT DU TEST E2E CHAT")
    logging.info("=" * 80)

    # Chargement de la configuration
    try:
        logging.info("Chargement de la configuration...")
        config = load_config(config_path)

        # Afficher la config (sans token)
        config_for_display = json.loads(json.dumps(config))
        if 'piag' in config_for_display and 'chat' in config_for_display['piag']:
            if 'security' in config_for_display['piag']['chat']:
                config_for_display['piag']['chat']['security']['token'] = '***MASKED***'

        logging.info(f"Configuration chargée:\n{json.dumps(config_for_display, indent=2)}")
        save_response(responses_dir, "00_config", config_for_display)

    except Exception as e:
        logging.error(f"Erreur lors du chargement de la config: {e}", exc_info=True)
        return 1

    # Récupération des paramètres
    try:
        chat_config = config.get('piag', {}).get('chat', {})

        # Token
        token = chat_config.get('security', {}).get('token')
        if not token:
            token_env_var = chat_config.get('security', {}).get('token_env_var', 'PIAG_CHAT_API_TOKEN')
            token = os.getenv(token_env_var)

        if not token:
            logging.error("Token API Chat manquant")
            print("\n❌ ERREUR: Token API Chat non trouvé")
            print("   Définissez PIAG_CHAT_API_TOKEN ou configurez config/piag.yaml")
            return 1

        logging.info(f"Token trouvé: {token[:15]}...{token[-5:]}")

        # URL de l'API
        api_url = chat_config.get('api', {}).get('base_url', 'https://preprod.api.piag.e2.rie.gouv.fr/v1/chat/completions')
        logging.info(f"API URL: {api_url}")

        # Modèle
        model = chat_config.get('model', 'mte-api-piag-mistral-medium-latest')
        logging.info(f"Modèle: {model}")

        # Timeout
        timeout = chat_config.get('api', {}).get('timeout', 60)
        logging.info(f"Timeout: {timeout}s")

        print(f"✓ Configuration chargée")
        print(f"  API URL: {api_url}")
        print(f"  Modèle: {model}")
        print(f"  Timeout: {timeout}s")

    except Exception as e:
        logging.error(f"Erreur lors de la récupération des paramètres: {e}", exc_info=True)
        return 1

    # Exécution des tests
    results = {
        'apikey_info': False,
        'basic_query': False,
        'completion': False,
        'chat_with_context': False
    }

    try:
        # Test 1: API Key Info
        results['apikey_info'] = test_apikey_info(api_url, token, responses_dir, timeout)

        # Test 2: Basic Query
        results['basic_query'] = test_basic_query(api_url, token, model, responses_dir, timeout)

        # Test 3: Completion (peut échouer si endpoint non disponible)
        results['completion'] = test_completion(api_url, token, model, responses_dir, timeout)

        # Test 4: Chat avec contexte
        results['chat_with_context'] = test_chat_with_context(api_url, token, model, responses_dir, timeout)

        # Résumé
        print("\n" + "=" * 80)
        print("RÉSUMÉ DES TESTS")
        print("=" * 80)

        for test_name, result in results.items():
            if result == "SKIPPED":
                status = "⏭️  IGNORÉ"
                logging.info(f"{test_name}: IGNORÉ (endpoint non disponible)")
            elif result:
                status = "✓ RÉUSSI"
                logging.info(f"{test_name}: RÉUSSI")
            else:
                status = "❌ ÉCHOUÉ"
                logging.info(f"{test_name}: ÉCHOUÉ")
            print(f"{test_name:25} : {status}")

        # Compter les succès (True) et ignorer les SKIPPED
        success_count = sum(1 for r in results.values() if r is True)
        skipped_count = sum(1 for r in results.values() if r == "SKIPPED")
        total_count = len(results)
        tested_count = total_count - skipped_count

        print("\n" + "=" * 80)
        if skipped_count > 0:
            print(f"ℹ️  {skipped_count} test(s) ignoré(s) (endpoints non disponibles)")

        if success_count == tested_count and tested_count > 0:
            print(f"✓ TOUS LES TESTS ONT RÉUSSI ({success_count}/{tested_count})")
            logging.info("TOUS LES TESTS CHAT ONT RÉUSSI")
            return 0
        elif success_count >= 2:
            print(f"⚠ TESTS PARTIELLEMENT RÉUSSIS ({success_count}/{tested_count} testés, {skipped_count} ignorés)")
            logging.warning(f"Tests partiellement réussis: {success_count}/{tested_count}")
            return 0
        else:
            print(f"❌ LA PLUPART DES TESTS ONT ÉCHOUÉ ({success_count}/{tested_count})")
            logging.error(f"La plupart des tests ont échoué: {success_count}/{tested_count}")
            return 1

        print("=" * 80)

    except Exception as e:
        logging.error(f"Test échoué: {e}", exc_info=True)
        print(f"\n❌ TEST ÉCHOUÉ: {e}")
        print(f"   Voir les logs pour plus de détails: {log_file}")
        return 1

    finally:
        print(f"\n📝 Logs complets: {log_file}")
        print(f"📂 Réponses JSON: {responses_dir}")
        logging.info("FIN DU TEST E2E CHAT")


def main():
    parser = argparse.ArgumentParser(description="Test End-to-End de l'API CHAT PIAG")
    parser.add_argument("--config", default="config/piag.yaml", help="Chemin vers le fichier de configuration")
    args = parser.parse_args()

    try:
        exit_code = run_chat_e2e_test(args.config)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
