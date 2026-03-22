"""Script pour mettre à jour tous les chemins de configuration RAG vers piag.rag.*"""
import re
from pathlib import Path

def fix_file(file_path):
    """Remplace les chemins de configuration dans un fichier."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Remplacements pour config.get()
    replacements = [
        (r"config\.get\('project', \{\}\)", "config.get('piag', {}).get('rag', {}).get('project', {})"),
        (r"config\.get\('security', \{\}\)", "config.get('piag', {}).get('rag', {}).get('security', {})"),
        (r"config\.get\('logging', \{\}\)", "config.get('piag', {}).get('rag', {}).get('logging', {})"),
        (r"config\.get\('api', \{\}\)", "config.get('piag', {}).get('rag', {}).get('api', {})"),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # Remplacement pour config.setdefault('logging', {})
    content = re.sub(
        r"config\.setdefault\('logging', \{\}\)",
        "config.setdefault('piag', {}).setdefault('rag', {}).setdefault('logging', {})",
        content
    )

    # Remplacement pour config['logging']
    content = re.sub(
        r"config\['logging'\]",
        "config.setdefault('piag', {}).setdefault('rag', {})['logging']",
        content
    )

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Mis à jour: {file_path.name}")
        return True
    else:
        print(f"  Aucun changement: {file_path.name}")
        return False

def main():
    """Traite tous les fichiers RAG."""
    commands_dir = Path('src/app/piag/commands')

    files_to_fix = [
        'piag_rag_collection_list.py',
        'piag_rag_collection_rm.py',
        'piag_rag_collection_update.py',
        'piag_rag_doc_chunks.py',
        'piag_rag_doc_get.py',
        'piag_rag_doc_list.py',
        'piag_rag_doc_rm.py',
        'piag_rag_doc_upload.py',
        'piag_rag_search.py',
    ]

    updated = 0
    for filename in files_to_fix:
        file_path = commands_dir / filename
        if file_path.exists():
            if fix_file(file_path):
                updated += 1
        else:
            print(f"✗ Fichier non trouvé: {filename}")

    print(f"\n{updated}/{len(files_to_fix)} fichier(s) mis à jour.")

if __name__ == '__main__':
    main()
