"""
CLI command to generate documents using external LLM APIs.

Usage: ambulon llm [OPTIONS]
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import List, Optional

from app.core.logging_config import setup_logging
from app.llm.core.config import (
    load_llm_config,
    get_api_key,
    get_base_url,
    get_provider_config,
    get_default_provider
)
from app.llm.core.manager import DocumentManager
from app.llm.core.providers import get_provider, list_providers

logger = logging.getLogger(__name__)


def collect_input_files(
    input_files: Optional[List[str]],
    input_dir: Optional[str]
) -> List[Path]:
    """
    Collect input files from arguments or directory.

    Args:
        input_files: List of file paths
        input_dir: Directory containing .md files

    Returns:
        List of Path objects

    Raises:
        ValueError: If no input files found
    """
    files = []

    # Add explicit input files
    if input_files:
        for file_str in input_files:
            path = Path(file_str)
            if path.is_file():
                files.append(path)
            else:
                logger.warning(f"Skipping non-file path: {file_str}")

    # Add files from input directory
    if input_dir:
        dir_path = Path(input_dir)
        if not dir_path.is_dir():
            raise ValueError(f"Input directory not found: {input_dir}")

        # Find all .md files
        md_files = list(dir_path.glob("*.md")) + list(dir_path.glob("*.markdown"))
        files.extend(md_files)
        logger.info(f"Found {len(md_files)} files in {input_dir}")

    if not files:
        raise ValueError("No input files specified. Use --input or --input-dir")

    return files


def main(argv=None):
    """
    Generate documents using LLM APIs.

    Args:
        argv: Arguments CLI ou None pour sys.argv

    Returns:
        Code de sortie (0 = succès, non-zéro = erreur)
    """
    parser = argparse.ArgumentParser(
        prog="ambulon llm",
        description="Generate documents using external LLM APIs (Kimi, ChatGPT, Claude).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy (priority from highest to lowest):
  1. Command-line arguments (--provider, --model, etc.)
  2. YAML configuration file (--config)
  3. Environment variables (KIMI_API_KEY, OPENAI_API_KEY, etc.)
  4. Default values

Environment Variables:
  KIMI_API_KEY          Kimi (Moonshot AI) API key
  OPENAI_API_KEY        OpenAI (ChatGPT) API key
  ANTHROPIC_API_KEY     Anthropic (Claude) API key

Examples:
  # Generate from multiple files
  ambulon llm -i doc1.md -i doc2.md -p prompt.md -o response.md

  # Generate from directory
  ambulon llm --input-dir ./docs -p prompt.md

  # Use specific provider
  ambulon llm -i docs/*.md -p prompt.md --provider chatgpt

  # Enable streaming
  ambulon llm -i doc.md -p prompt.md --stream

  # Use custom model
  ambulon llm -i doc.md -p prompt.md --model moonshot-v1-32k

See also:
  List providers: ambulon llm --list-providers
  Config file: config/llm.yaml
        """
    )

    # Input files
    parser.add_argument(
        "-i", "--input",
        action="append",
        dest="input_files",
        help="Input .md file (can be specified multiple times)"
    )

    parser.add_argument(
        "--input-dir",
        type=str,
        help="Directory containing input .md files"
    )

    # Prompt
    parser.add_argument(
        "-p", "--prompt",
        type=str,
        required=True,
        help="Prompt file (required)"
    )

    # Output
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file (default: response.md)"
    )

    # Provider settings
    parser.add_argument(
        "--provider",
        type=str,
        choices=["kimi", "chatgpt", "claude"],
        help="LLM provider to use (default: from config)"
    )

    parser.add_argument(
        "--model",
        type=str,
        help="Model name (provider-specific)"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="API key override (higher priority than config/env)"
    )

    # Generation settings
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Enable streaming output"
    )

    parser.add_argument(
        "--temperature",
        type=float,
        help="Sampling temperature (0.0-1.0)"
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        help="Maximum response tokens"
    )

    # Configuration
    parser.add_argument(
        "-c", "--config",
        type=str,
        help="Configuration file path (YAML)"
    )

    # Utility options
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="List available providers and exit"
    )

    # Logging
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args(argv)

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="llm")

    logger.info("[START] LLM document generation")

    try:
        # List providers if requested
        if args.list_providers:
            providers = list_providers()
            print("\nAvailable LLM providers:")
            for provider in providers:
                print(f"  - {provider}")
            print()
            return 0

        # Load configuration
        config = load_llm_config(args.config)

        # Determine provider
        provider_name = args.provider or get_default_provider(config)
        logger.info(f"Using provider: {provider_name}")

        # Get provider configuration
        provider_config = get_provider_config(provider_name, config)

        # Apply CLI overrides
        if args.api_key:
            provider_config["api_key"] = args.api_key
        if args.model:
            provider_config["model"] = args.model
        if args.temperature is not None:
            provider_config["temperature"] = args.temperature
        if args.max_tokens is not None:
            provider_config["max_tokens"] = args.max_tokens

        # Get API key and base URL
        api_key = get_api_key(provider_name, config)
        base_url = get_base_url(provider_name, config)

        # Collect input files
        input_files = collect_input_files(args.input_files, args.input_dir)
        prompt_file = Path(args.prompt)

        # Determine output file
        output_file = Path(args.output) if args.output else Path(config["llm"]["output"]["default_file"])

        logger.info(f"Input files: {len(input_files)}")
        logger.info(f"Prompt: {prompt_file}")
        logger.info(f"Output: {output_file}")

        # Initialize manager
        manager = DocumentManager(config["llm"])

        # Validate inputs
        manager.validate_inputs(input_files, prompt_file)

        # Load documents
        documents = manager.load_documents(input_files)

        # Load prompt
        prompt = manager.load_prompt(prompt_file)

        # Aggregate content
        context = manager.aggregate_content(documents)

        logger.info(f"Aggregated context: {len(context)} characters")

        # Initialize provider
        provider = get_provider(
            name=provider_name,
            api_key=api_key,
            base_url=base_url,
            config=provider_config
        )

        # Display summary
        print(f"\n📄 LLM Generation Summary")
        print(f"   Provider: {provider_name}")
        print(f"   Model: {provider_config.get('model')}")
        print(f"   Input files: {len(input_files)}")
        for f in input_files:
            print(f"     - {f.name}")
        print(f"   Prompt: {prompt_file.name}")
        print(f"   Output: {output_file}")
        print(f"   Streaming: {'Yes' if args.stream else 'No'}")
        print("\n" + "=" * 70)

        # Generate
        start_time = time.time()

        if args.stream:
            print(f"\n🚀 Generating (streaming)...\n")

            # Stream generation
            full_content = []
            try:
                for chunk in provider.generate_stream(
                    prompt=prompt,
                    context=context,
                    model=args.model,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens
                ):
                    print(chunk, end='', flush=True)
                    full_content.append(chunk)

                print("\n")  # New line at end

                content = ''.join(full_content)
                tokens = {"total_tokens": 0}  # Streaming doesn't return token count

            except Exception as e:
                logger.error(f"Generation error: {e}", exc_info=True)
                print(f"\n❌ Generation failed: {e}")
                return 1

        else:
            print(f"\n🚀 Generating...\n")

            # Non-streaming generation
            try:
                result = provider.generate(
                    prompt=prompt,
                    context=context,
                    model=args.model,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens
                )

                content = result["content"]
                tokens = result["tokens"]

                # Display response preview
                preview_length = 200
                preview = content[:preview_length] + "..." if len(content) > preview_length else content
                print(preview)
                print()

            except Exception as e:
                logger.error(f"Generation error: {e}", exc_info=True)
                print(f"\n❌ Generation failed: {e}")
                return 1

        duration = time.time() - start_time

        # Save response
        metadata = manager.create_metadata(
            provider=provider_name,
            model=provider_config.get("model"),
            input_files=input_files,
            prompt_file=prompt_file,
            output_file=output_file,
            tokens=tokens,
            duration=duration,
            streaming=args.stream,
            success=True
        )

        manager.save_response(content, output_file, metadata)

        # Success
        print(f"✅ Generation completed successfully!")
        print(f"   Output: {output_file}")
        print(f"   Duration: {duration:.2f}s")
        if not args.stream:
            print(f"   Tokens: {tokens.get('total_tokens', 0)}")
        print(f"   Content length: {len(content)} characters")

        return 0

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration error: {e}")
        return 1
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"\n❌ File not found: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Please check the logs for more details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
