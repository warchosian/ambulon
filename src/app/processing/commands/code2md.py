"""
Module CLI pour encapsuler du contenu dans des blocs de code Markdown.
Supporte la détection automatique du format ou spécification explicite.
"""

import sys
import argparse
import re
from pathlib import Path
from typing import Optional

from app.core.output_paths import format_output_path
# Mapping des extensions vers formats
EXTENSION_TO_FORMAT = {
    '.py': 'python',
    '.sh': 'bash',
    '.bash': 'bash',
    '.zsh': 'zsh',
    '.fish': 'fish',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.xml': 'xml',
    '.html': 'html',
    '.htm': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.sql': 'sql',
    '.md': 'markdown',
    '.txt': 'text',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.cs': 'csharp',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.r': 'r',
    '.m': 'matlab',
    '.plantuml': 'plantuml',
    '.puml': 'plantuml',
    '.mermaid': 'mermaid',
    '.dot': 'graphviz',
    '.graphviz': 'graphviz',
}

# Formats supportés
SUPPORTED_FORMATS = [
    'text', 'bash', 'sh', 'python', 'javascript', 'typescript', 'json', 'yaml',
    'xml', 'html', 'css', 'scss', 'sql', 'markdown', 'java', 'c', 'cpp',
    'csharp', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin', 'r', 'matlab',
    'plantuml', 'mermaid', 'graphviz', 'dot', 'zsh', 'fish',
]


def detect_format_from_extension(file_path: Path) -> Optional[str]:
    """
    Détecte le format à partir de l'extension du fichier.

    Args:
        file_path: Chemin du fichier

    Returns:
        Format détecté ou None
    """
    ext = file_path.suffix.lower()
    return EXTENSION_TO_FORMAT.get(ext)


def detect_format_from_content(content: str) -> str:
    """
    Détecte le format à partir du contenu.

    Args:
        content: Contenu à analyser

    Returns:
        Format détecté (fallback sur 'text')
    """
    lines = content.strip().split('\n')

    if not lines:
        return 'text'

    first_line = lines[0].strip()

    # Détection shebang
    if first_line.startswith('#!'):
        if 'python' in first_line:
            return 'python'
        elif 'bash' in first_line or 'sh' in first_line:
            return 'bash'
        elif 'node' in first_line:
            return 'javascript'
        elif 'ruby' in first_line:
            return 'ruby'
        elif 'php' in first_line:
            return 'php'

    # Détection JSON
    if content.strip().startswith('{') or content.strip().startswith('['):
        try:
            import json
            json.loads(content)
            return 'json'
        except (ValueError, json.JSONDecodeError):
            pass

    # Détection YAML (commence souvent par '---' ou contient des clés avec ':')
    if first_line == '---' or re.search(r'^\w+:', content, re.MULTILINE):
        if not content.strip().startswith('<'):  # Pas du HTML/XML
            return 'yaml'

    # Détection XML/HTML
    if content.strip().startswith('<?xml') or content.strip().startswith('<!DOCTYPE'):
        return 'xml'
    if content.strip().startswith('<html') or content.strip().startswith('<!DOCTYPE html'):
        return 'html'

    # Détection PlantUML
    if '@startuml' in content or '@startmindmap' in content:
        return 'plantuml'

    # Détection Mermaid
    if any(keyword in content for keyword in ['graph TD', 'graph LR', 'sequenceDiagram', 'classDiagram', 'stateDiagram']):
        return 'mermaid'

    # Détection GraphViz
    if 'digraph' in content or 'graph {' in content:
        return 'graphviz'

    # Détection SQL (mots-clés)
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE TABLE', 'ALTER TABLE', 'DROP TABLE']
    if any(keyword in content.upper() for keyword in sql_keywords):
        return 'sql'

    # Détection Python (mots-clés)
    python_keywords = ['def ', 'class ', 'import ', 'from ', 'if __name__']
    if any(keyword in content for keyword in python_keywords):
        return 'python'

    # Fallback
    return 'text'


def wrap_content_in_markdown(content: str, format_type: str) -> str:
    """
    Encapsule le contenu dans un bloc de code Markdown.

    Args:
        content: Contenu à encapsuler
        format_type: Type de format pour la coloration syntaxique

    Returns:
        Contenu encapsulé en Markdown
    """
    # S'assurer que le contenu se termine par un saut de ligne
    if not content.endswith('\n'):
        content += '\n'

    return f"```{format_type}\n{content}```\n"


def main(argv=None):
    """
    Point d'entrée principal pour la commande code2md.

    Args:
        argv: Arguments CLI (list of str), ou None pour utiliser sys.argv

    Returns:
        int: Code de sortie (0 = succès, 1 = erreur)
    """
    parser = argparse.ArgumentParser(
        description="Encapsule du contenu dans des blocs de code Markdown avec coloration syntaxique.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Format auto-détecté → génère script.python.md
  ambulon code2md script.py

  # Format auto-détecté → génère data.json.md
  ambulon code2md data.json

  # Format explicite
  ambulon code2md script.py -t python

  # Sortie personnalisée
  ambulon code2md script.py -o README.md

  # Depuis stdin vers stdout
  cat config.yaml | ambulon code2md -t yaml

  # Depuis stdin vers fichier
  cat script.sh | ambulon code2md -t bash -o script.bash.md

Formats supportés:
  text, bash, sh, python, javascript, typescript, json, yaml, xml, html, css,
  sql, markdown, java, c, cpp, go, rust, ruby, php, plantuml, mermaid, graphviz, etc.
        """
    )

    parser.add_argument("input_file", nargs='?', type=Path, help="Fichier d'entrée à encapsuler (omettez pour lire depuis stdin).")
    parser.add_argument("-t", "--type", "--format", dest="format", default="auto", help="Format du code (auto, text, bash, python, json, yaml, etc.). Défaut: auto.")
    parser.add_argument("-o", "--output", type=Path, help="Fichier de sortie. Si omis avec fichier d'entrée, génère <nom>.<format>.md.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Mode verbeux (affiche le format détecté).")

    args = parser.parse_args(argv)

    # Lecture du contenu
    if args.input_file:
        if not args.input_file.exists():
            print(f"Erreur: Le fichier n'existe pas: {args.input_file}", file=sys.stderr)
            return 1

        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier: {e}", file=sys.stderr)
            return 1
    else:
        # Lecture depuis stdin
        if sys.stdin.isatty():
            print("Erreur: Aucun fichier spécifié et aucune donnée en stdin.", file=sys.stderr)
            print("Usage: ambulon code2md <fichier> [options]", file=sys.stderr)
            print("   ou: cat fichier | ambulon code2md -t <format>", file=sys.stderr)
            return 1

        try:
            content = sys.stdin.read()
        except Exception as e:
            print(f"Erreur lors de la lecture de stdin: {e}", file=sys.stderr)
            return 1

    # Détermination du format
    if args.format == "auto":
        # Tentative de détection depuis l'extension
        if args.input_file:
            detected_format = detect_format_from_extension(args.input_file)
            if detected_format:
                format_type = detected_format
            else:
                # Détection depuis le contenu
                format_type = detect_format_from_content(content)
        else:
            # Pas de fichier, détection depuis le contenu uniquement
            format_type = detect_format_from_content(content)

        if args.verbose:
            print(f"[INFO] Format détecté automatiquement: {format_type}", file=sys.stderr)
    else:
        format_type = args.format.lower()

        if format_type not in SUPPORTED_FORMATS:
            print(f"[WARNING] Format non reconnu: {format_type}. Utilisation du format tel quel.", file=sys.stderr)

    # Encapsulation
    markdown_content = wrap_content_in_markdown(content, format_type)

    # Détermination du fichier de sortie
    if args.output:
        output_file = args.output
    elif args.input_file:
        # Génération automatique: <nom>.<format>.md dans le même répertoire
        output_file = args.input_file.parent / f"{args.input_file.stem}.{format_type}.md"
    else:
        # Stdin sans -o : sortie sur stdout
        print(markdown_content, end='')
        return 0

    # Écriture du fichier de sortie
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        if args.verbose:
            print(f"[SUCCESS] Fichier généré: {format_output_path(output_file)}", file=sys.stderr)
        else:
            print(f"Fichier généré: {format_output_path(output_file)}")

        return 0

    except Exception as e:
        print(f"Erreur lors de l'écriture du fichier: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
