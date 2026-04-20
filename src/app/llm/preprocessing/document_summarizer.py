#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intelligent document summarizer using LLM.

Summarizes large code documentation files by:
- Chunking content into manageable pieces
- Using LLM to summarize each chunk
- Combining summaries into a cohesive overview
"""

import re
import sys
from pathlib import Path
import yaml

# Import LLM providers
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from app.llm.core.providers import get_provider

# Default chunk size (in characters)
CHUNK_SIZE = 50000


def load_llm_config():
    """Load LLM configuration from config file."""
    config_path = Path(__file__).parent.parent.parent.parent.parent / 'config' / 'llm.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def chunk_content(content, chunk_size=CHUNK_SIZE):
    """
    Split content into chunks by file sections.

    Args:
        content: Full file content
        chunk_size: Maximum size per chunk (characters)

    Returns:
        list: List of content chunks
    """
    # Find all file sections - use a more flexible pattern for emoji
    # Pattern matches: ### [emoji or space] `filename` [size octets]
    file_pattern = r'(###\s+.{1,3}\s*`[^`]+`\s*\[\d+\s+octets\].*?)(?=###\s+.{1,3}\s*`|$)'
    file_sections = re.findall(file_pattern, content, re.DOTALL)

    chunks = []
    current_chunk = ""

    for section in file_sections:
        # If adding this section exceeds chunk size, save current chunk
        if len(current_chunk) + len(section) > chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = ""

        current_chunk += section + "\n\n"

    # Add remaining content
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def summarize_chunk(provider, chunk, chunk_num, total_chunks):
    """
    Summarize a single chunk using LLM.

    Args:
        provider: LLM provider instance
        chunk: Content chunk to summarize
        chunk_num: Current chunk number
        total_chunks: Total number of chunks

    Returns:
        str: Summary text
    """
    prompt = f"""Tu es un expert en analyse de code. Analyse le chunk {chunk_num}/{total_chunks} d'un projet et produis un résumé structuré.

Pour chaque fichier important dans ce chunk, identifie:
1. **Type de fichier**: Configuration, Code source, Script, Documentation, etc.
2. **Rôle**: Quelle est sa fonction dans le projet ?
3. **Points clés**: Technologies utilisées, dépendances, patterns, etc.

Ignore les fichiers triviaux (.gitkeep, fichiers vides).
Sois concis mais précis. Format Markdown."""

    context = f"""# Chunk {chunk_num}/{total_chunks}

{chunk}
"""

    print(f"  Résumé du chunk {chunk_num}/{total_chunks}...")

    result = provider.generate(
        prompt=prompt,
        context=context,
        max_tokens=2000
    )

    return result['content']


def summarize_document(input_file, output_file, chunk_size=CHUNK_SIZE):
    """
    Summarize large code documentation file using LLM.

    Args:
        input_file: Path to input code.md file
        output_file: Path to output summary file
        chunk_size: Size of content chunks (characters)

    Returns:
        dict: Statistics about summarization operation
    """
    print("Chargement de la configuration LLM...")
    config = load_llm_config()

    # Get provider config
    default_provider = config['llm']['default_provider']
    provider_config = config['llm']['providers'][default_provider]

    print(f"Utilisation du provider: {default_provider}")
    print(f"Modèle: {provider_config['model']}")

    # Extract API key (handle ${VAR:-default} format)
    api_key = provider_config['api_key']
    if api_key.startswith('${'):
        # Extract default value
        api_key = api_key.split(':-')[1].rstrip('}')

    # Initialize provider
    provider = get_provider(
        name=default_provider,
        api_key=api_key,
        base_url=provider_config['base_url'],
        config=provider_config
    )

    print(f"Lecture du fichier: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract header and arborescence - more flexible pattern for emoji
    header_match = re.search(r'^(.*?)##\s+.{1,3}\s*Arborescence des fichiers', content, re.DOTALL)
    header = header_match.group(1) if header_match else ""

    arbo_match = re.search(
        r'##\s+.{1,3}\s*Arborescence des fichiers(.*?)##\s+.{1,3}\s*Contenu des fichiers',
        content, re.DOTALL
    )
    arborescence = arbo_match.group(0) if arbo_match else ""

    # Extract file content section - flexible pattern
    content_match = re.search(r'##\s+.{1,3}\s*Contenu des fichiers(.*)', content, re.DOTALL)
    file_content = content_match.group(1) if content_match else ""

    # Chunk the content
    print("Découpage en chunks...")
    chunks = chunk_content(file_content, chunk_size)
    print(f"  {len(chunks)} chunks créés")

    # Summarize each chunk
    print("Génération des résumés...")
    summaries = []
    for i, chunk in enumerate(chunks, 1):
        try:
            summary = summarize_chunk(provider, chunk, i, len(chunks))
            summaries.append(f"## Résumé Chunk {i}/{len(chunks)}\n\n{summary}\n\n")
        except Exception as e:
            print(f"  Erreur sur chunk {i}: {e}")
            summaries.append(f"## Résumé Chunk {i}/{len(chunks)}\n\n*[Erreur de génération: {e}]*\n\n")

    # Generate global summary
    print("Génération du résumé global...")
    combined_summaries = "\n".join(summaries)

    global_prompt = """Tu es un expert en architecture logicielle. À partir des résumés de chunks ci-dessous, produis un résumé global du projet en 3 sections:

1. **Architecture globale**: Structure du projet, composants principaux
2. **Stack technique**: Technologies, frameworks, outils utilisés
3. **Points d'attention**: Configuration, dépendances, patterns notables

Sois synthétique mais complet. Format Markdown."""

    try:
        global_result = provider.generate(
            prompt=global_prompt,
            context=f"# Résumés des chunks\n\n{combined_summaries}",
            max_tokens=3000
        )
        global_summary = global_result['content']
    except Exception as e:
        print(f"  Erreur génération résumé global: {e}")
        global_summary = "*[Erreur de génération]*"

    # Build output
    output_content = f"""{header}
## 📁 Arborescence des fichiers

{arborescence.split('## 📄 Contenu des fichiers')[0]}

---

## 🤖 Résumé Global par IA

{global_summary}

---

## 📝 Résumés détaillés par chunks

{combined_summaries}

---

## ℹ️ Note

Ce document a été généré automatiquement par analyse IA du fichier code source.
Les résumés sont basés sur l'analyse de {len(chunks)} chunks du code original.
Provider: {default_provider} - Modèle: {provider_config['model']}
"""

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)

    stats = {
        'chunks': len(chunks),
        'provider': default_provider,
        'model': provider_config['model']
    }

    return stats


def main():
    """CLI entry point."""
    if len(sys.argv) != 3:
        print("Usage: python document_summarizer.py <input_file> <output_file>")
        print("Example: python document_summarizer.py sireines.code.md sireines.code.summary.md")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        stats = summarize_document(input_file, output_file)

        print(f"\n✓ Extraction terminée!")
        print(f"  Chunks analysés: {stats['chunks']}")
        print(f"  Provider: {stats['provider']}")
        print(f"  Modèle: {stats['model']}")
        print(f"  Fichier de sortie: {output_file}")
    except Exception as e:
        print(f"\n✗ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
