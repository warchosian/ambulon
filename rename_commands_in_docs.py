"""Script pour renommer les commandes RAG dans la documentation."""
import os
from pathlib import Path

# Dictionnaire des remplacements
replacements = {
    'piag-collection-add': 'piag-rag-collection-add',
    'piag-collection-list': 'piag-rag-collection-list',
    'piag-collection-get': 'piag-rag-collection-get',
    'piag-collection-update': 'piag-rag-collection-update',
    'piag-collection-rm': 'piag-rag-collection-rm',
    'piag-doc-upload': 'piag-rag-doc-upload',
    'piag-doc-list': 'piag-rag-doc-list',
    'piag-doc-get': 'piag-rag-doc-get',
    'piag-doc-rm': 'piag-rag-doc-rm',
    'piag-doc-chunks': 'piag-rag-doc-chunks',
    'piag-search': 'piag-rag-search',
}

def process_file(file_path):
    """Traite un fichier en remplaçant les anciens noms par les nouveaux."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        for old, new in replacements.items():
            content = content.replace(old, new)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Mis à jour: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Erreur avec {file_path}: {e}")
        return False

def main():
    """Parcourt tous les fichiers .md et applique les remplacements."""
    root_dir = Path('.')
    updated_count = 0

    for md_file in root_dir.rglob('*.md'):
        if process_file(md_file):
            updated_count += 1

    print(f"\n{updated_count} fichier(s) mis à jour.")

if __name__ == '__main__':
    main()
