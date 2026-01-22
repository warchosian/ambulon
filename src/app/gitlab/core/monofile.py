"""Helpers to generate monofile Markdown outputs from cloned repositories."""
from pathlib import Path
from typing import Optional, Tuple
import logging

from app.processing.core.project_to_md_converter import project_to_markdown_logic
from app.conversion.commands.md2html import process_markdown_to_html
from app.processing.core.markdown_flattener import flatten_markdown_directory_logic
from app.processing.core.markdown_merger import fusion_markdown_files_logic

logger = logging.getLogger(__name__)


def infer_repo_mode(repo_dir: Path) -> str:
    """Return 'wiki' if repo dir looks like a wiki repo, otherwise 'code'."""
    name = repo_dir.name.lower()
    if name.endswith(".wiki"):
        return "wiki"
    return "code"


def _resolve_output_path(
    repo_dir: Path,
    output_dir: Optional[Path],
    filename_template: Optional[str],
    default_name: str,
) -> Path:
    target_dir = output_dir if output_dir else (repo_dir.parent / f"{repo_dir.name}.rag")
    target_dir.mkdir(parents=True, exist_ok=True)
    name = default_name
    if filename_template:
        name = filename_template.replace("{project}", repo_dir.name)
    return target_dir / name


def generate_code_monofile(
    repo_dir: Path,
    output_dir: Optional[Path] = None,
    filename_template: Optional[str] = None,
) -> Tuple[int, Optional[Path]]:
    """Generate <repo>.code.md using project2md logic."""
    output_file = _resolve_output_path(
        repo_dir=repo_dir,
        output_dir=output_dir,
        filename_template=filename_template,
        default_name=f"{repo_dir.name}.code.md",
    )
    logger.info(f"Generating code monofile for {repo_dir} -> {output_file}")
    exit_code, md_path = project_to_markdown_logic(directory=repo_dir, output_file=output_file)
    if exit_code == 0 and md_path:
        html_path = md_path.with_suffix(".html")
        html_code = process_markdown_to_html(str(md_path), str(html_path), verbose=False, standalone=True)
        if html_code == 0:
            logger.info(f"HTML created: {html_path}")
        else:
            logger.error(f"Failed to generate HTML for {md_path}")
            return 1, md_path
    return exit_code, md_path


def generate_wiki_monofile(
    repo_dir: Path,
    output_dir: Optional[Path] = None,
    filename_template: Optional[str] = None,
    flatten_dir: Optional[Path] = None,
) -> Tuple[int, Optional[Path]]:
    """Generate <repo>.md from a wiki repo using flatten-md + merge-md."""
    output_file = _resolve_output_path(
        repo_dir=repo_dir,
        output_dir=output_dir,
        filename_template=filename_template,
        default_name=f"{repo_dir.name}.md",
    )
    if flatten_dir is None:
        base_dir = output_dir if output_dir else (repo_dir.parent / f"{repo_dir.name}.rag")
        base_dir.mkdir(parents=True, exist_ok=True)
        flatten_dir = base_dir / f"{repo_dir.name}-flattened"

    logger.info(f"Flattening wiki repo {repo_dir} -> {flatten_dir}")
    exit_code, flattened_path = flatten_markdown_directory_logic(
        source_dir=repo_dir,
        output_dir=flatten_dir,
    )
    if exit_code != 0 or not flattened_path:
        # No Markdown files or flattening failed; treat as skip to avoid hard failure.
        logger.warning(f"No Markdown files to flatten for wiki repo: {repo_dir}")
        return 0, None

    logger.info(f"Merging flattened wiki -> {output_file}")
    exit_code, md_path = fusion_markdown_files_logic(
        source_dir=flattened_path,
        output_file=output_file,
        output_name=output_file.name,
        title=f"Wiki: {repo_dir.name}",
    )
    if exit_code == 0 and md_path:
        html_path = md_path.with_suffix(".html")
        html_code = process_markdown_to_html(str(md_path), str(html_path), verbose=False, standalone=True)
        if html_code == 0:
            logger.info(f"HTML created: {html_path}")
        else:
            logger.error(f"Failed to generate HTML for {md_path}")
            return 1, md_path
    return exit_code, md_path


def generate_monofile(
    repo_dir: Path,
    mode: Optional[str] = None,
    output_dir: Optional[Path] = None,
    filename_template: Optional[str] = None,
) -> Tuple[int, Optional[Path]]:
    """Generate a monofile from a repo directory (code or wiki)."""
    effective_mode = mode or infer_repo_mode(repo_dir)
    if effective_mode == "wiki":
        return generate_wiki_monofile(
            repo_dir=repo_dir,
            output_dir=output_dir,
            filename_template=filename_template,
        )
    return generate_code_monofile(
        repo_dir=repo_dir,
        output_dir=output_dir,
        filename_template=filename_template,
    )
