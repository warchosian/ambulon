#!/usr/bin/env python3
"""
Test simple du vérificateur de configuration (sans réseau)
"""
import sys
from pathlib import Path

# Test des imports
try:
    import yaml
    print("✓ PyYAML disponible:", yaml.__version__)
except ImportError as e:
    print("❌ PyYAML manquant:", e)
    sys.exit(1)

# Test de lecture de la config
config_path = Path("config/piag.yaml")
if not config_path.exists():
    print(f"❌ Fichier de config introuvable: {config_path}")
    sys.exit(1)

print(f"✓ Fichier de config trouvé: {config_path}")

# Charger la config
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print("✓ Configuration YAML chargée avec succès")
except Exception as e:
    print(f"❌ Erreur lors du chargement: {e}")
    sys.exit(1)

# Vérifier la structure
print("\n" + "=" * 80)
print("VÉRIFICATION DE LA STRUCTURE")
print("=" * 80)

# Structure RAG
rag_config = config.get('piag', {}).get('rag', {})
print(f"\n[RAG]")
print(f"  ✓ Base URL: {rag_config.get('api', {}).get('base_url', 'NON DÉFINIE')}")
print(f"  ✓ Timeout: {rag_config.get('api', {}).get('timeout', 'NON DÉFINI')}s")

token_rag = rag_config.get('security', {}).get('token', '')
if token_rag:
    print(f"  ✓ Token RAG: {token_rag[:15]}...{token_rag[-5:]}")
else:
    print(f"  ❌ Token RAG: NON DÉFINI")

project_id = rag_config.get('project', {}).get('project_id', '')
if project_id:
    print(f"  ✓ Project ID: {project_id}")
else:
    print(f"  ❌ Project ID: NON DÉFINI")

# Structure CHAT
chat_config = config.get('piag', {}).get('chat', {})
print(f"\n[CHAT]")
print(f"  ✓ Base URL: {chat_config.get('api', {}).get('base_url', 'NON DÉFINIE')}")
print(f"  ✓ Timeout: {chat_config.get('api', {}).get('timeout', 'NON DÉFINI')}s")
print(f"  ✓ Modèle: {chat_config.get('model', 'NON DÉFINI')}")

token_chat = chat_config.get('security', {}).get('token', '')
if token_chat:
    print(f"  ✓ Token CHAT: {token_chat[:15]}...{token_chat[-5:]}")
else:
    print(f"  ❌ Token CHAT: NON DÉFINI")

# Résumé
print("\n" + "=" * 80)
print("RÉSUMÉ")
print("=" * 80)

issues = []
if not token_rag:
    issues.append("Token RAG manquant")
if not project_id:
    issues.append("Project ID manquant")
if not token_chat:
    issues.append("Token CHAT manquant")

if not issues:
    print("\n✓ Configuration complète et valide")
    print("\nVous pouvez lancer les tests E2E:")
    print("  python test_piag_rag_e2e.py")
    print("  python test_piag_chat_e2e.py")
    print("  python test_piag_all.py")
    sys.exit(0)
else:
    print(f"\n❌ {len(issues)} problème(s) détecté(s):")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    sys.exit(1)
