"""Script pour mettre à jour les chemins de configuration dans les commandes RAG."""
import os
import re
from pathlib import Path

def fix_config_paths(file_path):
    """Remplace config.get('xxx') par config.get('piag').get('rag').get('xxx')"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Remplacements pour les accès à la config
    replacements = [
        # config.get('project', {}) → config.get('piag', {}).get('rag', {}).get('project', {})
        (r"config\.get\('project', \{\}\)", "config.get('piag', {}).get('rag', {}).get('project', {})"),

        # config.get('security', {}) → config.get('piag', {}).get('rag', {}).get('security', {})
        (r"config\.get\('security', \{\}\)", "config.get('piag', {}).get('rag', {}).get('security', {})"),

        # config.get('logging', {}) → config.get('piag', {}).get('rag', {}).get('logging', {})
        (r"config\.get\('logging', \{\}\)", "config.get('piag', {}).get('rag', {}).get('logging', {})"),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # Remplacements pour les modifications directes de config
    # if 'logging' not in config: → if 'piag' not in config:
    if "'logging' not in config" in content:
        content = content.replace(
            "if 'logging' not in config:\n            config['logging'] = {}\n        config['logging']['enable_debug'] = True\n        config['logging']['log_requests'] = True\n        config['logging']['log_responses'] = True",
            "if 'piag' not in config:\n            config['piag'] = {}\n        if 'rag' not in config['piag']:\n            config['piag']['rag'] = {}\n        if 'logging' not in config['piag']['rag']:\n            config['piag']['rag']['logging'] = {}\n        config['piag']['rag']['logging']['enable_debug'] = True\n        config['piag']['rag']['logging']['log_requests'] = True\n        config['piag']['rag']['logging']['log_responses'] = True"
        )

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Mis à jour: {file_path}")
        return True
    else:
        print(f"  Aucun changement: {file_path}")
        return False

def main():
    """Parcourt toutes les commandes RAG et applique les correctifs."""
    commands_dir = Path('src/app/piag/commands')
    updated = 0

    for file in commands_dir.glob('piag_rag_*.py'):
        if file.name == 'piag_rag_collection_add.py':
            print(f"  Ignoré (déjà modifié): {file}")
            continue
        if fix_config_paths(file):
            updated += 1

    print(f"\n{updated} fichier(s) mis à jour.")

if __name__ == '__main__':
    main()
