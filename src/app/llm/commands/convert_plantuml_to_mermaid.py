#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert PlantUML diagrams to Mermaid in prompt files.

Usage:
    ambulon plantuml2mermaid -i input.md
    ambulon plantuml2mermaid -d workplace-ambulon/piag-chat/prompts
"""

import argparse
import logging
import re
import sys
from pathlib import Path
import io
import yaml

# Force UTF-8 encoding for stdout/stderr on Windows
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Import LLM provider
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.llm.core.providers import get_provider

logger = logging.getLogger(__name__)


def load_llm_config():
    """Load LLM configuration from config file."""
    config_path = Path(__file__).parent.parent.parent.parent.parent / 'config' / 'llm.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def convert_plantuml_to_mermaid_regex(plantuml_code):
    """
    Convert PlantUML diagram to Mermaid using regex (basic conversion).

    This is a simplified converter focusing on common patterns.
    Complex diagrams may need manual adjustment.
    """
    # Remove PlantUML specific commands
    code = plantuml_code
    code = re.sub(r'@startuml.*?\n', '', code)
    code = re.sub(r'@enduml.*?\n', '', code)
    code = re.sub(r'skinparam.*?\n', '', code)
    code = re.sub(r'title\s+(.+)', r'---\ntitle: \1\n---', code)
    code = re.sub(r'legend\s+right.*?endlegend', '', code, flags=re.DOTALL)
    code = re.sub(r'legend\s+left.*?endlegend', '', code, flags=re.DOTALL)

    # Convert actors to participants for sequence diagrams
    code = re.sub(r'actor\s+"([^"]+)"\s+as\s+(\w+)', r'participant \2 as \1', code)

    # Convert packages/rectangles to subgraphs
    code = re.sub(r'package\s+"([^"]+)"\s+as\s+(\w+)\s+#\w+\s*\{', r'subgraph \2["\1"]', code)
    code = re.sub(r'package\s+"([^"]+)"\s*\{', r'subgraph [\1]', code)
    code = re.sub(r'\}', r'end', code)

    # Convert rectangle to simple nodes
    code = re.sub(r'rectangle\s+"([^"]+)"\s+as\s+(\w+)', r'\2["\1"]', code)

    # Convert arrows
    code = re.sub(r'(\w+)\s+-->\s+(\w+)\s*:\s*(.+)', r'\1 -->|\3| \2', code)
    code = re.sub(r'(\w+)\s+-->\s+(\w+)', r'\1 --> \2', code)
    code = re.sub(r'(\w+)\s+-\[dashed\]->\s+(\w+)\s*:\s*(.+)', r'\1 -.->|\3| \2', code)
    code = re.sub(r'(\w+)\s+-\[dashed\]->\s+(\w+)', r'\1 -.-> \2', code)

    # Convert notes (basic)
    code = re.sub(r'note\s+(right|left|top|bottom)\s+of\s+\w+.*?end note', '', code, flags=re.DOTALL)

    # Clean up empty lines
    lines = [line for line in code.split('\n') if line.strip()]

    # Add graph type if not present
    if not any(line.strip().startswith('graph') or line.strip().startswith('flowchart')
               or line.strip().startswith('sequenceDiagram') for line in lines):
        lines.insert(0, 'graph TB')

    return '\n'.join(lines)


def convert_plantuml_to_mermaid_llm(plantuml_code, provider):
    """
    Convert PlantUML diagram to Mermaid using LLM (intelligent conversion).

    Args:
        plantuml_code: PlantUML source code
        provider: LLM provider instance

    Returns:
        Mermaid diagram code
    """
    prompt = """Tu es un expert en diagrammes techniques. Convertis le diagramme PlantUML suivant en syntaxe Mermaid équivalente.

Règles de conversion :
1. Préserve la structure et la sémantique du diagramme
2. Utilise la syntaxe Mermaid idiomatique (graph TB, flowchart, sequenceDiagram, etc.)
3. Adapte les styles et couleurs aux capacités de Mermaid
4. Convertis les packages PlantUML en subgraphs Mermaid
5. Préserve les labels et annotations
6. Utilise des emojis si le diagramme original en contient
7. Ne retourne QUE le code Mermaid, sans explications ni balises markdown

IMPORTANT : Réponds UNIQUEMENT avec le code Mermaid pur, sans ```mermaid ni aucune autre annotation."""

    context = f"""Diagramme PlantUML à convertir :

```plantuml
{plantuml_code}
```

Convertis ce diagramme en syntaxe Mermaid équivalente."""

    logger.debug("Calling LLM for PlantUML conversion...")

    try:
        result = provider.generate(
            prompt=prompt,
            context=context,
            max_tokens=2000,
            temperature=0.3  # Lower temperature for more consistent output
        )

        mermaid_code = result['content'].strip()

        # Clean up if LLM returned markdown code blocks
        mermaid_code = re.sub(r'^```mermaid\s*\n', '', mermaid_code)
        mermaid_code = re.sub(r'\n```\s*$', '', mermaid_code)
        mermaid_code = mermaid_code.strip()

        return mermaid_code

    except Exception as e:
        logger.error(f"LLM conversion failed: {e}")
        logger.warning("Falling back to regex conversion")
        return convert_plantuml_to_mermaid_regex(plantuml_code)


def process_file(input_file, output_file=None, mode='llm', provider=None):
    """
    Convert PlantUML diagrams to Mermaid in a markdown file.

    Args:
        input_file: Input markdown file path
        output_file: Output file path (default: input.mmd.md)
        mode: Conversion mode ('llm' or 'regex')
        provider: LLM provider instance (required if mode='llm')

    Returns:
        dict: Statistics about conversion
    """
    if not output_file:
        input_path = Path(input_file)
        stem = input_path.stem
        output_file = input_path.parent / f"{stem}.mmd.md"

    logger.info(f"Converting {input_file} -> {output_file} (mode: {mode})")

    # Try multiple encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    content = None
    used_encoding = None

    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                content = f.read()
            used_encoding = encoding
            if encoding != 'utf-8':
                logger.warning(f"File {input_file} read with {encoding} encoding")
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if content is None:
        raise ValueError(f"Could not decode file {input_file} with any supported encoding")

    stats = {
        'plantuml_blocks': 0,
        'mermaid_blocks': 0,
        'plantuml_references': 0,
        'mermaid_references': 0
    }

    # Convert PlantUML code blocks to Mermaid
    def replace_plantuml(match):
        stats['plantuml_blocks'] += 1
        plantuml_code = match.group(1)

        if mode == 'llm':
            mermaid_code = convert_plantuml_to_mermaid_llm(plantuml_code, provider)
        else:
            mermaid_code = convert_plantuml_to_mermaid_regex(plantuml_code)

        stats['mermaid_blocks'] += 1
        return f"```mermaid\n{mermaid_code}\n```"

    # Replace ```plantuml blocks
    content = re.sub(
        r'```plantuml\s*\n(.*?)\n```',
        replace_plantuml,
        content,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Replace references to PlantUML with Mermaid
    replacements = [
        (r'\bPlantUML\b', 'Mermaid'),
        (r'\bplantuml\b', 'mermaid'),
        (r'@startuml/@enduml', 'mermaid code blocks'),
        (r'`@startuml`/`@enduml`', '`mermaid` code blocks'),
        (r'syntaxe PlantUML', 'syntaxe Mermaid'),
        (r'diagrammes? PlantUML', 'diagrammes Mermaid'),
        (r'diagramme en PlantUML', 'diagramme en Mermaid'),
        (r'format PlantUML', 'format Mermaid'),
        (r'REGLES_PLANTUML\.md', 'REGLES_MERMAID.md'),
        (r'règles? PlantUML', 'règles Mermaid'),
    ]

    for pattern, replacement in replacements:
        before = content
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if content != before:
            stats['plantuml_references'] += content.count(replacement) - before.count(replacement)
            stats['mermaid_references'] += content.count(replacement) - before.count(replacement)

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return stats


def main(args=None):
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert PlantUML diagrams to Mermaid in prompt files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ambulon plantuml2mermaid -i prompt.dat.md
  ambulon plantuml2mermaid -d workplace-ambulon/piag-chat/prompts
  ambulon plantuml2mermaid -i input.md -o output.mmd.md

Note:
  This performs basic conversion. Complex diagrams may need manual review.
"""
    )

    parser.add_argument(
        '-i', '--input',
        metavar='FILE',
        help='Input markdown file'
    )

    parser.add_argument(
        '-d', '--directory',
        metavar='DIR',
        help='Process all .md files in directory (creates .mmd.md versions)'
    )

    parser.add_argument(
        '-o', '--output',
        metavar='FILE',
        help='Output file (default: <input>.mmd.md)'
    )

    parser.add_argument(
        '--mode',
        choices=['llm', 'regex'],
        default='llm',
        help='Conversion mode: llm (intelligent, default) or regex (fast, basic)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parsed_args = parser.parse_args(args)

    # Configure logging
    log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if not parsed_args.input and not parsed_args.directory:
        parser.error("Either --input or --directory is required")

    if parsed_args.input and parsed_args.directory:
        parser.error("Cannot specify both --input and --directory")

    print(f"\n📄 PlantUML to Mermaid Converter")
    print(f"   Mode: {parsed_args.mode.upper()} "
          f"({'🤖 AI-powered' if parsed_args.mode == 'llm' else '⚡ Fast regex-based'})")
    print("=" * 70)

    # Initialize LLM provider if needed
    provider = None
    if parsed_args.mode == 'llm':
        try:
            print("\n🔧 Loading LLM configuration...")
            config = load_llm_config()
            default_provider = config['llm']['default_provider']
            provider_config = config['llm']['providers'][default_provider]

            # Extract API key (handle ${VAR:-default} format)
            api_key = provider_config['api_key']
            if api_key.startswith('${'):
                api_key = api_key.split(':-')[1].rstrip('}')

            provider = get_provider(
                name=default_provider,
                api_key=api_key,
                base_url=provider_config['base_url'],
                config=provider_config
            )

            print(f"   Provider: {default_provider}")
            print(f"   Model: {provider_config['model']}\n")
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider: {e}")
            print(f"\n⚠️  Warning: LLM initialization failed, falling back to regex mode")
            print(f"   Error: {e}\n")
            parsed_args.mode = 'regex'

    try:
        total_stats = {
            'files_processed': 0,
            'plantuml_blocks': 0,
            'mermaid_blocks': 0,
            'plantuml_references': 0,
            'mermaid_references': 0
        }

        # Process directory
        if parsed_args.directory:
            directory = Path(parsed_args.directory)
            if not directory.exists():
                logger.error(f"Directory not found: {directory}")
                sys.exit(1)

            md_files = list(directory.glob('*.md'))
            # Exclude already converted .mmd.md files
            md_files = [f for f in md_files if not f.name.endswith('.mmd.md')]

            if not md_files:
                print(f"\n⚠️  No .md files found in {directory}")
                return 0

            print(f"\n🔍 Found {len(md_files)} markdown files")
            print(f"   Directory: {directory}\n")

            for md_file in md_files:
                print(f"   Processing: {md_file.name}")
                try:
                    stats = process_file(md_file, mode=parsed_args.mode, provider=provider)
                    total_stats['files_processed'] += 1
                    total_stats['plantuml_blocks'] += stats['plantuml_blocks']
                    total_stats['mermaid_blocks'] += stats['mermaid_blocks']
                    total_stats['plantuml_references'] += stats['plantuml_references']
                    total_stats['mermaid_references'] += stats['mermaid_references']

                    if stats['plantuml_blocks'] > 0 or stats['plantuml_references'] > 0:
                        print(f"      → Converted {stats['plantuml_blocks']} diagrams, "
                              f"{stats['plantuml_references']} references")
                except Exception as e:
                    logger.error(f"Failed to process {md_file.name}: {e}")
                    print(f"      ⚠️  Skipped: {e}")

        # Process single file
        else:
            input_file = parsed_args.input
            output_file = parsed_args.output

            if not Path(input_file).exists():
                logger.error(f"Input file not found: {input_file}")
                sys.exit(1)

            print(f"\n   Input: {input_file}")
            print(f"   Output: {output_file or Path(input_file).stem + '.mmd.md'}\n")

            stats = process_file(input_file, output_file, mode=parsed_args.mode, provider=provider)
            total_stats['files_processed'] = 1
            total_stats['plantuml_blocks'] = stats['plantuml_blocks']
            total_stats['mermaid_blocks'] = stats['mermaid_blocks']
            total_stats['plantuml_references'] = stats['plantuml_references']
            total_stats['mermaid_references'] = stats['mermaid_references']

        # Display summary
        print(f"\n✓ Conversion completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   Files processed: {total_stats['files_processed']}")
        print(f"   PlantUML diagrams converted: {total_stats['plantuml_blocks']}")
        print(f"   Mermaid diagrams created: {total_stats['mermaid_blocks']}")
        print(f"   Text references updated: {total_stats['plantuml_references']}")

        logger.info(f"[SUCCESS] Conversion completed")

    except Exception as e:
        logger.error(f"[ERROR] Conversion failed: {e}", exc_info=parsed_args.verbose)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
