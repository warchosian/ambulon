#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document filter for code.md files.

Filters large code documentation files by:
- Keeping complete file tree structure
- Filtering important file types (.java, .xml, .yml, .md, etc.)
- Prioritizing key files (README, pom.xml, configuration files)
- Excluding binary/generated files (.oom, .pdm, .xdb, .rptdesign)
"""

import re
import sys
from pathlib import Path

# Important file extensions to keep
IMPORTANT_EXTENSIONS = [
    '.java', '.xml', '.yml', '.yaml', '.md', '.properties',
    '.json', '.sql', '.sh', '.py', '.ts', '.js', '.jsx', '.tsx',
    '.html', '.css', '.scss', '.env'
]

# Extensions to exclude (binary/generated files)
EXCLUDE_EXTENSIONS = [
    '.oom', '.pdm', '.xdb', '.rptdesign', '.set',
    '.jar', '.war', '.ear', '.class', '.zip'
]

# Top priority files to always keep
TOP_FILES = [
    'README.md', 'pom.xml', '.gitlab-ci.yml', 'docker-compose',
    'Dockerfile', 'application.properties', 'settings.xml',
    'package.json', 'tsconfig.json', '.env'
]


def is_important_file(filename):
    """Check if file is important based on name or extension."""
    filename_lower = filename.lower()

    # Check if it's a top priority file
    for top in TOP_FILES:
        if top.lower() in filename_lower:
            return True

    # Check extension
    ext = Path(filename).suffix.lower()
    return ext in IMPORTANT_EXTENSIONS


def is_excluded_file(filename):
    """Check if file should be excluded."""
    ext = Path(filename).suffix.lower()
    return ext in EXCLUDE_EXTENSIONS


def filter_document(input_file, output_file, max_file_size=5000):
    """
    Filter large code documentation file.

    Args:
        input_file: Path to input code.md file
        output_file: Path to output filtered file
        max_file_size: Maximum file size to keep full content (bytes)

    Returns:
        dict: Statistics about filtering operation
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract header (before arborescence) - more flexible pattern
    header_match = re.search(r'^(.*?)##\s+.{1,3}\s*Arborescence des fichiers', content, re.DOTALL)
    header = header_match.group(1) if header_match else ""

    # Find arborescence section - more flexible pattern for emoji
    arbo_match = re.search(
        r'##\s+.{1,3}\s*Arborescence des fichiers(.*?)##\s+.{1,3}\s*Contenu des fichiers',
        content, re.DOTALL
    )
    arborescence = arbo_match.group(0) if arbo_match else ""

    # Find all file sections - use a more flexible pattern
    # Pattern matches: ### [emoji or space] `filename` [size octets]
    file_pattern = r'###\s+.{1,3}\s*`([^`]+)`\s*\[(\d+)\s+octets\](.*?)(?=###\s+.{1,3}\s*`|$)'
    file_sections = re.finditer(file_pattern, content, re.DOTALL)

    filtered_files = []
    stats = {
        'total': 0,
        'kept': 0,
        'excluded': 0,
        'omitted': 0,
        'total_size': 0,
        'kept_size': 0
    }

    for match in file_sections:
        filepath = match.group(1)
        size = int(match.group(2))
        file_content = match.group(3)

        stats['total'] += 1
        stats['total_size'] += size

        filename = Path(filepath).name

        # Determine action for this file
        if is_excluded_file(filename):
            stats['excluded'] += 1
            # Keep header only for excluded files
            filtered_files.append(
                f"### 📄 `{filepath}` [{size} octets]\n\n"
                f"*[Fichier exclu - type binaire/généré]*\n\n"
            )
        elif is_important_file(filename) or size < max_file_size:
            stats['kept'] += 1
            stats['kept_size'] += size
            # Keep full content
            filtered_files.append(f"### 📄 `{filepath}` [{size} octets]{file_content}\n\n")
        else:
            stats['omitted'] += 1
            # Keep header only
            filtered_files.append(
                f"### 📄 `{filepath}` [{size} octets]\n\n"
                f"*[Contenu omis - fichier non prioritaire]*\n\n"
            )

    # Calculate reduction percentage
    reduction_pct = (1 - stats['kept_size'] / stats['total_size']) * 100 if stats['total_size'] > 0 else 0

    # Build output
    output_content = f"""{header}
## 📁 Arborescence des fichiers

{arborescence.split('## 📄 Contenu des fichiers')[0]}

---

## 📊 Statistiques d'extraction

- **Fichiers analysés**: {stats['total']}
- **Fichiers conservés (contenu complet)**: {stats['kept']}
- **Fichiers exclus (binaires/générés)**: {stats['excluded']}
- **Fichiers omis (non prioritaires)**: {stats['omitted']}
- **Taille totale originale**: {stats['total_size']:,} octets (~{stats['total_size']/1024/1024:.1f} MB)
- **Taille conservée**: {stats['kept_size']:,} octets (~{stats['kept_size']/1024/1024:.1f} MB)
- **Réduction**: {reduction_pct:.1f}%

---

## 📄 Contenu des fichiers (filtré)

{"".join(filtered_files)}
"""

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)

    return stats


def main():
    """CLI entry point."""
    if len(sys.argv) != 3:
        print("Usage: python document_filter.py <input_file> <output_file>")
        print("Example: python document_filter.py sireines.code.md sireines.code.filtered.md")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print(f"Filtrage du document: {input_file}")
    stats = filter_document(input_file, output_file)

    print(f"\n✓ Extraction terminée!")
    print(f"  Fichiers totaux: {stats['total']}")
    print(f"  Fichiers conservés: {stats['kept']}")
    print(f"  Fichiers exclus: {stats['excluded']}")
    print(f"  Fichiers omis: {stats['omitted']}")
    print(f"  Taille originale: {stats['total_size']/1024/1024:.1f} MB")
    print(f"  Taille extraite: {stats['kept_size']/1024/1024:.1f} MB")
    print(f"  Réduction: {(1 - stats['kept_size']/stats['total_size'])*100:.1f}%")
    print(f"  Fichier de sortie: {output_file}")


if __name__ == "__main__":
    main()
