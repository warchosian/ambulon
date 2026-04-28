"""
CLI command to batch generate documentation from prompts for all applications.

Usage: ambulon generate-docs [OPTIONS]
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from app.core.logging_config import setup_logging
from app.llm.core.config import (
    load_llm_config,
    get_api_key,
    get_base_url,
    get_provider_config,
    get_default_provider
)
from app.llm.core.manager import DocumentManager
from app.llm.core.providers import get_provider

logger = logging.getLogger(__name__)


def extract_prompt_name(prompt_path: Path) -> str:
    """
    Extract prompt name from file path.

    Examples:
        prompt.dex.md -> dex
        prompt.dat_c4model.md -> dat_c4model

    Args:
        prompt_path: Path to prompt file

    Returns:
        Extracted prompt name
    """
    name = prompt_path.stem  # Get filename without extension

    # Remove "prompt." prefix
    if name.startswith("prompt."):
        return name[7:]  # len("prompt.") = 7
    else:
        return name


def extract_app_name(rag_dir: Path) -> str:
    """
    Extract application name from .rag directory path.

    Example:
        workplace-ambulon/gitlab/sireines.rag -> sireines

    Args:
        rag_dir: Path to .rag directory

    Returns:
        Application name
    """
    return rag_dir.stem.replace(".rag", "")


def find_prompts(prompts_dir: Path) -> List[Path]:
    """
    Find all prompt files in prompts directory.

    Looks for files matching: prompt.*.md

    Args:
        prompts_dir: Directory containing prompts

    Returns:
        List of prompt file paths
    """
    if not prompts_dir.exists():
        logger.warning(f"Prompts directory not found: {prompts_dir}")
        return []

    # Find prompt.*.md files (including .mmd.md Mermaid diagrams)
    prompts = list(prompts_dir.glob("prompt.*.md"))

    # Sort by name
    prompts.sort(key=lambda x: x.name)

    logger.info(f"Found {len(prompts)} prompts in {prompts_dir}")
    return prompts


def find_applications(gitlab_dir: Path) -> List[Path]:
    """
    Find all .rag directories in gitlab directory.

    Args:
        gitlab_dir: Directory containing .rag directories

    Returns:
        List of .rag directory paths
    """
    if not gitlab_dir.exists():
        logger.warning(f"GitLab directory not found: {gitlab_dir}")
        return []

    rag_dirs = [d for d in gitlab_dir.iterdir() if d.is_dir() and d.name.endswith(".rag")]
    rag_dirs.sort(key=lambda x: x.name)

    logger.info(f"Found {len(rag_dirs)} applications in {gitlab_dir}")
    return rag_dirs


def check_rag_files(rag_dir: Path, app_name: str) -> Optional[list]:
    """
    Check if required RAG files exist for an application.

    Args:
        rag_dir: Path to .rag directory
        app_name: Application name

    Returns:
        List of context files (filtered, summarized, wiki, wikisi) or None if missing required files
    """
    # Try filtered/summarized first (sireines)
    filtered_file = rag_dir / f"{app_name}.code.filtered.md"
    summarized_file = rag_dir / f"{app_name}.code.summarized.md"

    # Fallback to enhanced/base (admin_ep)
    enhanced_file = rag_dir / f"{app_name}.code.enhanced.md"
    base_file = rag_dir / f"{app_name}.code.md"

    context_files = None

    if filtered_file.exists() and summarized_file.exists():
        context_files = [filtered_file, summarized_file]
    elif enhanced_file.exists() and base_file.exists():
        context_files = [base_file, enhanced_file]
    elif base_file.exists():
        context_files = [base_file]
    else:
        logger.debug(f"No code files found for {app_name}")
        return None

    # Add optional files if they exist
    wiki_file = rag_dir / f"{app_name}.wiki.md"
    if wiki_file.exists():
        context_files.append(wiki_file)

    wikisi_file = rag_dir / f"{app_name}.wikisi.md"
    if wikisi_file.exists():
        context_files.append(wikisi_file)

    return context_files


def generate_document(
    prompt_path: Path,
    context_files: List[Path],
    output_path: Path,
    provider_name: str,
    config: Dict,
    manager: DocumentManager,
    verbose: bool = False
) -> bool:
    """
    Generate a single document using LLM.

    Args:
        prompt_path: Path to prompt file
        context_files: List of context files (.code.filtered.md, .code.summarized.md)
        output_path: Path for output file
        provider_name: Name of LLM provider
        config: LLM configuration
        manager: DocumentManager instance
        verbose: Enable verbose output

    Returns:
        True if successful, False otherwise
    """
    try:
        # Map local_* providers to 'local' for the provider system
        actual_provider = provider_name
        if provider_name.startswith("local_"):
            actual_provider = "local"

        # But keep original provider name for config lookup to get correct model
        config_provider = provider_name

        # Get provider configuration (use original name to get specific model config)
        provider_config = get_provider_config(config_provider, config)
        api_key = get_api_key(actual_provider, config)
        base_url = get_base_url(actual_provider, config)

        # Load prompt
        prompt = manager.load_prompt(prompt_path)

        # Load context documents
        documents = manager.load_documents(context_files)

        # Aggregate context
        context = manager.aggregate_content(documents)

        # Initialize provider (use mapped name for provider system)
        provider = get_provider(
            name=actual_provider,
            api_key=api_key,
            base_url=base_url,
            config=provider_config
        )

        # Generate
        start_time = time.time()

        result = provider.generate(
            prompt=prompt,
            context=context,
            model=provider_config.get("model")
        )

        content = result["content"]
        tokens = result["tokens"]
        duration = time.time() - start_time

        # Save response
        metadata = manager.create_metadata(
            provider=provider_name,
            model=provider_config.get("model"),
            input_files=context_files,
            prompt_file=prompt_path,
            output_file=output_path,
            tokens=tokens,
            duration=duration,
            streaming=False,
            success=True
        )

        manager.save_response(content, output_path, metadata)

        logger.info(f"Generated: {output_path.name} ({len(content)} chars, {duration:.1f}s)")
        return True

    except Exception as e:
        logger.error(f"Failed to generate {output_path.name}: {e}", exc_info=verbose)
        return False


def main(argv=None):
    """
    Batch generate documentation from prompts for all applications.

    Args:
        argv: CLI arguments or None for sys.argv

    Returns:
        Exit code (0 = success, non-zero = error)
    """
    parser = argparse.ArgumentParser(
        prog="ambulon generate-docs",
        description="Batch generate documentation from prompts for all applications.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Process:
  1. Scan all prompts in workplace-ambulon/piag-chat/prompts/
  2. For each application with a .rag directory
  3. Check if .code.filtered.md and .code.summarized.md exist
  4. Generate workplace-ambulon/gitlab/<app-name>.<prompt-name>.md

Examples:
  # Generate all documents
  ambulon generate-docs

  # Generate for specific prompt
  ambulon generate-docs --prompt dex

  # Generate for specific application
  ambulon generate-docs --app sireines

  # Use specific provider
  ambulon generate-docs --provider claude

  # Dry run (show what would be generated)
  ambulon generate-docs --dry-run
        """
    )

    # Directories
    parser.add_argument(
        "--prompts-dir",
        type=Path,
        default=None,
        help="Directory containing prompt files (default: from config)"
    )

    parser.add_argument(
        "--gitlab-dir",
        type=Path,
        default=None,
        help="Directory containing .rag directories (default: from config)"
    )

    parser.add_argument(
        "--livrables-dir",
        type=Path,
        default=None,
        help="Directory for output files (default: from config)"
    )

    # Filters
    parser.add_argument(
        "--prompt",
        type=str,
        help="Generate only for specific prompt (e.g., 'dex', 'ccf')"
    )

    parser.add_argument(
        "--app",
        type=str,
        help="Generate only for specific application (e.g., 'sireines')"
    )

    # Provider settings
    parser.add_argument(
        "--provider",
        choices=["kimi", "kimi_k2", "chatgpt", "claude", "local", "local_llama3_1_8b", "local_qwen2_5_1_5b", "local_phi3_mini", "local_gpt_oss_120b", "local_gpt_oss_20b", "local_qwen3_coder_480b", "local_deepseek_v3_1_671b", "gemini", "alibaba", "cloud_kimi", "cloud_kimi_k2", "cloud_glm", "cloud_glm_4_7", "cloud_qwen", "cloud_deepseek", "cloud_deepseek_v4", "cloud_claude", "cloud_chatgpt", "cloud_gemini", "cloud_gpt_oss_120b", "cloud_gpt_oss_20b", "cloud_qwen3_coder_480b", "cloud_deepseek_v3_1_671b"],
        help="LLM provider to use (default: from config)"
    )

    # Configuration
    parser.add_argument(
        "-c", "--config",
        type=str,
        help="Configuration file path (YAML). Use llm_local.yaml for local providers."
    )

    # Options
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without actually generating"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output files"
    )

    parser.add_argument(
        "--skip-errors",
        action="store_true",
        help="Continue processing even if some generations fail"
    )

    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip confirmation prompt and proceed with generation"
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
    setup_logging(level=log_level, log_file_prefix="generate_docs")

    logger.info("[START] Batch document generation")

    try:
        # Load configuration
        config = load_llm_config(args.config)

        # Resolve paths from config if not provided as arguments
        paths_config = config.get("llm", {}).get("paths", {})

        if not args.prompts_dir:
            args.prompts_dir = Path(paths_config.get("prompts_dir", "workplace-ambulon/piag-chat/prompts"))
        if not args.gitlab_dir:
            args.gitlab_dir = Path(paths_config.get("gitlab_dir", "workplace-ambulon/gitlab"))
        if not args.livrables_dir:
            args.livrables_dir = Path(paths_config.get("delivrables_dir", "workplace-ambulon/delivrables"))

        # Determine provider
        provider_name = args.provider or get_default_provider(config)

        # If 'local' is requested, pick the first available local provider
        if provider_name == "local":
            local_providers = [k for k in config["llm"]["providers"].keys() if k.startswith("local_")]
            if local_providers:
                provider_name = local_providers[0]
                logger.info(f"'local' resolved to: {provider_name}")
            else:
                raise ValueError("No local providers configured. Available providers: " + ", ".join(config["llm"]["providers"].keys()))

        logger.info(f"Using provider: {provider_name}")

        # Initialize manager
        manager = DocumentManager(config["llm"])

        # Find prompts
        prompts = find_prompts(args.prompts_dir)
        if not prompts:
            print(f"\n❌ No prompts found in {args.prompts_dir}")
            return 1

        # Filter prompts if requested
        if args.prompt:
            prompts = [p for p in prompts if extract_prompt_name(p) == args.prompt]
            if not prompts:
                print(f"\n❌ Prompt '{args.prompt}' not found")
                return 1

        # Find applications
        applications = find_applications(args.gitlab_dir)
        if not applications:
            print(f"\n❌ No .rag directories found in {args.gitlab_dir}")
            return 1

        # Filter applications if requested
        if args.app:
            applications = [a for a in applications if extract_app_name(a) == args.app]
            if not applications:
                print(f"\n❌ Application '{args.app}' not found")
                return 1

        # Build generation plan
        generation_plan = []

        for prompt_path in prompts:
            prompt_name = extract_prompt_name(prompt_path)

            for rag_dir in applications:
                app_name = extract_app_name(rag_dir)

                # Check if RAG files exist
                context_files = check_rag_files(rag_dir, app_name)

                if context_files:
                    # Get model name for suffix from the provider config
                    # Use original provider name (e.g., local_llama3.1:8b) to get specific model config
                    provider_config = get_provider_config(provider_name, config)
                    model_name = provider_config.get("model", provider_name).replace(":", "_").replace("/", "_")
                    output_filename = f"{app_name}.{prompt_name}.{model_name}.md"
                    output_path = args.livrables_dir / output_filename

                    # Check if already exists
                    if output_path.exists() and not args.force:
                        logger.debug(f"Skipping existing: {output_path.name}")
                        continue

                    generation_plan.append({
                        "prompt_path": prompt_path,
                        "prompt_name": prompt_name,
                        "app_name": app_name,
                        "context_files": context_files,
                        "output_path": output_path
                    })

        # Display plan before execution
        print(f"\n📋 Generation Plan")
        print(f"   Provider: {provider_name}")
        print(f"   Config:")
        print(f"     Prompts: {args.prompts_dir}")
        print(f"     RAG:    {args.gitlab_dir}")
        print(f"     Output: {args.livrables_dir}")
        print(f"   Prompts: {len(prompts)}")
        print(f"   Applications: {len(applications)}")
        print(f"   Documents to generate: {len(generation_plan)}")

        # Show input and output files for each document
        print("\n📁 Fichiers:")
        project_root = Path.cwd()
        for item in generation_plan:
            # Resolve paths to absolute first, then make relative to project root
            prompt_abs = item["prompt_path"].resolve()
            output_abs = item["output_path"].resolve()
            prompt_rel = prompt_abs.relative_to(project_root)
            output_rel = output_abs.relative_to(project_root)

            # Only show files actually used (from context_files)
            rag_files_rel = [str(f.resolve().relative_to(project_root)) for f in item["context_files"]]

            # Print all paths
            print(f"   Output: {output_rel}")
            print(f"     Prompt: {prompt_rel}")
            print(f"     Input: {', '.join(sorted(rag_files_rel))}")

        if args.dry_run:
            print("\n🔍 Dry Run - Documents that would be generated:")
            project_root = Path.cwd()
            for item in generation_plan:
                # Resolve paths to absolute first, then make relative to project root
                prompt_abs = item["prompt_path"].resolve()
                output_abs = item["output_path"].resolve()
                prompt_rel = prompt_abs.relative_to(project_root)
                output_rel = output_abs.relative_to(project_root)
                # Only show files actually used (from context_files)
                rag_files_rel = [str(f.resolve().relative_to(project_root)) for f in item["context_files"]]
                print(f"   Output: {output_rel}")
                print(f"     Prompt: {prompt_rel}")
                print(f"     Input: {', '.join(sorted(rag_files_rel))}")
            print()
            return 0

        if not generation_plan:
            print("\n✓ Nothing to generate (all documents exist or no matching applications)")
            print("  Use --force to regenerate existing documents")
            return 0

        # Confirm generation (skip if --force or --yes is set)
        if len(generation_plan) > 10 and not args.force and not args.yes:
            print(f"\n⚠️  About to generate {len(generation_plan)} documents")
            response = input("Continue? [y/N] ")
            if response.lower() != 'y':
                print("Cancelled.")
                return 0

        print("\n" + "=" * 70)
        print(f"🚀 Starting generation...\n")

        # Generate documents
        success_count = 0
        error_count = 0

        project_root = Path.cwd()
        for idx, item in enumerate(generation_plan, 1):
            # Resolve paths to absolute first, then make relative to project root
            prompt_abs = item["prompt_path"].resolve()
            output_abs = item["output_path"].resolve()
            prompt_rel = prompt_abs.relative_to(project_root)
            output_rel = output_abs.relative_to(project_root)
            # Only show files actually used (from context_files)
            rag_files_rel = [str(f.resolve().relative_to(project_root)) for f in item["context_files"]]
            print(f"[{idx}/{len(generation_plan)}] {output_rel}")
            print(f"  Prompt: {prompt_rel}")
            print(f"  Input: {', '.join(sorted(rag_files_rel))}", end=' ', flush=True)

            success = generate_document(
                prompt_path=item["prompt_path"],
                context_files=item["context_files"],
                output_path=item["output_path"],
                provider_name=provider_name,
                config=config,
                manager=manager,
                verbose=args.verbose
            )

            if success:
                print("✓")
                success_count += 1
            else:
                print("✗")
                error_count += 1

                if not args.skip_errors:
                    print(f"\n❌ Generation failed. Use --skip-errors to continue on errors.")
                    return 1

            time.sleep(1)

        # Summary
        print("\n" + "=" * 70)
        print(f"\n✅ Generation completed!")
        print(f"   Success: {success_count}")
        if error_count > 0:
            print(f"   Errors: {error_count}")
        print(f"   Output directory: {args.gitlab_dir}")

        return 0 if error_count == 0 else 1

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Please check the logs for more details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
