"""CLI command to generate monofile Markdown from a cloned repository directory."""
import argparse
import logging
import sys
from pathlib import Path

from app.core.logging_config import setup_logging
from app.gitlab.core.monofile import generate_monofile

logger = logging.getLogger(__name__)


def main(argv=None):
    """
    Generate a monofile from a cloned repo directory.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments
    2. Default values
    """
    parser = argparse.ArgumentParser(
        description="Generate a monofile Markdown (and HTML) from a cloned repository directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect mode (code or wiki) and output in <repo>.rag directory
  ambulon gitlab-monofile G:\\repos\\my-project

  # Explicit wiki mode, custom output dir
  ambulon gitlab-monofile G:\\repos\\my-project.wiki --mode wiki -o G:\\out

  # Custom filename template
  ambulon gitlab-monofile G:\\repos\\my-project --name "{project}.code.md"
  # HTML is generated alongside the Markdown output
        """
    )

    parser.add_argument("repo_dir", type=Path, help="Path to the cloned repository directory.")
    parser.add_argument(
        "--mode",
        choices=["code", "wiki", "both", "auto"],
        default="auto",
        help="Force mode (code, wiki, both). Default: auto-detect from directory name."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output directory for the monofile (default: <repo>.rag directory)."
    )
    parser.add_argument(
        "--name",
        dest="filename_template",
        help="Filename template, e.g. '{project}.code.md' or '{project}.md'."
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress most output messages.")

    args = parser.parse_args(argv)

    if not args.repo_dir.exists():
        print(f"Error: Directory does not exist: {args.repo_dir}", file=sys.stderr)
        return 1
    if not args.repo_dir.is_dir():
        print(f"Error: Path is not a directory: {args.repo_dir}", file=sys.stderr)
        return 1

    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="gitlab_monofile")

    outputs = []
    if args.mode == "both":
        code_exit, code_output = generate_monofile(
            repo_dir=args.repo_dir,
            mode="code",
            output_dir=args.output,
            filename_template=args.filename_template or "{project}.code.md",
        )
        wiki_exit, wiki_output = generate_monofile(
            repo_dir=args.repo_dir,
            mode="wiki",
            output_dir=args.output,
            filename_template=args.filename_template or "{project}.md",
        )
        if code_output:
            outputs.append(code_output)
        if wiki_output:
            outputs.append(wiki_output)
        exit_code = 0 if code_exit == 0 and wiki_exit == 0 else 1
    else:
        mode = None if args.mode == "auto" else args.mode
        exit_code, output_path = generate_monofile(
            repo_dir=args.repo_dir,
            mode=mode,
            output_dir=args.output,
            filename_template=args.filename_template,
        )
        if output_path:
            outputs.append(output_path)

    if exit_code == 0 and outputs:
        print(f"\n✓ Monofile generated!")
        for output_path in outputs:
            try:
                relative_path = output_path.relative_to(Path.cwd())
            except ValueError:
                relative_path = output_path.resolve()
            print(f"Fichier produit : {relative_path}")
            html_path = Path(str(output_path)).with_suffix(".html")
            if html_path.exists():
                try:
                    html_relative = html_path.relative_to(Path.cwd())
                except ValueError:
                    html_relative = html_path.resolve()
                print(f"Fichier produit : {html_relative}")
        return 0

    logger.error("Monofile generation failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
