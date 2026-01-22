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


def _base_project_name(repo_dir: Path) -> str:
    name = repo_dir.name
    return name[:-5] if name.lower().endswith(".wiki") else name


def _resolve_base_dir(
    repo_dir: Path,
    output_dir: Optional[Path],
    output_mode: str,
) -> Path:
    if output_dir:
        return output_dir
    if output_mode == "shared":
        return repo_dir.parent / f"{_base_project_name(repo_dir)}.rag"
    return repo_dir.parent / f"{repo_dir.name}.rag"


def _resolve_output_path(
    repo_dir: Path,
    output_dir: Optional[Path],
    output_mode: str,
    filename_template: Optional[str],
    default_name: str,
) -> Path:
    target_dir = _resolve_base_dir(repo_dir, output_dir, output_mode)
    target_dir.mkdir(parents=True, exist_ok=True)
    name = default_name
    if filename_template:
        name = filename_template.replace("{project}", repo_dir.name)
    return target_dir / name


def _resolve_templates(config: dict, default_templates: list[str]) -> list[str]:
    templates = config.get("templates")
    if isinstance(templates, list) and templates:
        return [str(t) for t in templates]
    filename_template = config.get("filename_template")
    if filename_template:
        return [str(filename_template)]
    return default_templates


def _materialize_template_paths(
    repo_dir: Path,
    base_dir: Path,
    templates: list[str],
) -> tuple[list[Path], list[Path]]:
    md_targets: list[Path] = []
    html_targets: list[Path] = []
    for template in templates:
        name = template.replace("{project}", repo_dir.name)
        target = base_dir / name
        if name.lower().endswith(".md"):
            md_targets.append(target)
        elif name.lower().endswith(".html"):
            html_targets.append(target)
    return md_targets, html_targets


def generate_code_monofile(
    repo_dir: Path,
    output_dir: Optional[Path] = None,
    output_mode: str = "separate",
    filename_template: Optional[str] = None,
    templates: Optional[list[str]] = None,
) -> Tuple[int, Optional[Path]]:
    """Generate <repo>.code.md using project2md logic."""
    base_dir = _resolve_base_dir(repo_dir, output_dir, output_mode)
    base_dir.mkdir(parents=True, exist_ok=True)
    templates_list = templates if templates is not None else [filename_template] if filename_template else None
    if not templates_list:
        templates_list = [f"{repo_dir.name}.code.md", f"{repo_dir.name}.code.html"]
    md_targets, html_targets = _materialize_template_paths(repo_dir, base_dir, templates_list)

    # Always generate a markdown file to feed HTML conversion
    md_output = md_targets[0] if md_targets else (base_dir / f"{repo_dir.name}.code.md")
    logger.info(f"Generating code monofile for {repo_dir} -> {md_output}")
    exit_code, md_path = project_to_markdown_logic(directory=repo_dir, output_file=md_output)
    if exit_code != 0 or not md_path:
        return exit_code, md_path

    # Convert to HTML for each requested .html target
    for html_target in html_targets:
        html_code = process_markdown_to_html(str(md_path), str(html_target), verbose=False, standalone=True)
        if html_code == 0:
            logger.info(f"HTML created: {html_target}")
        else:
            logger.error(f"Failed to generate HTML for {md_path}")
            return 1, md_path

    # If no .md template requested, remove the generated md
    if not md_targets:
        try:
            md_path.unlink(missing_ok=True)
        except Exception:
            pass

    return 0, md_path


def generate_wiki_monofile(
    repo_dir: Path,
    output_dir: Optional[Path] = None,
    output_mode: str = "separate",
    filename_template: Optional[str] = None,
    templates: Optional[list[str]] = None,
    flatten_dir: Optional[Path] = None,
) -> Tuple[int, Optional[Path]]:
    """Generate <repo>.md from a wiki repo using flatten-md + merge-md."""
    base_dir = _resolve_base_dir(repo_dir, output_dir, output_mode)
    base_dir.mkdir(parents=True, exist_ok=True)
    templates_list = templates if templates is not None else [filename_template] if filename_template else None
    if not templates_list:
        templates_list = [f"{repo_dir.name}.md", f"{repo_dir.name}.html"]
    md_targets, html_targets = _materialize_template_paths(repo_dir, base_dir, templates_list)
    output_file = md_targets[0] if md_targets else (base_dir / f"{repo_dir.name}.md")
    if flatten_dir is None:
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
    if exit_code != 0 or not md_path:
        return exit_code, md_path

    for html_target in html_targets:
        html_code = process_markdown_to_html(str(md_path), str(html_target), verbose=False, standalone=True)
        if html_code == 0:
            logger.info(f"HTML created: {html_target}")
        else:
            logger.error(f"Failed to generate HTML for {md_path}")
            return 1, md_path

    if not md_targets:
        try:
            md_path.unlink(missing_ok=True)
        except Exception:
            pass

    return 0, md_path


def generate_monofile(
    repo_dir: Path,
    mode: Optional[str] = None,
    output_dir: Optional[Path] = None,
    output_mode: str = "separate",
    filename_template: Optional[str] = None,
    templates: Optional[list[str]] = None,
) -> Tuple[int, Optional[Path]]:
    """Generate a monofile from a repo directory (code or wiki)."""
    effective_mode = mode or infer_repo_mode(repo_dir)
    if effective_mode == "wiki":
        return generate_wiki_monofile(
            repo_dir=repo_dir,
            output_dir=output_dir,
            output_mode=output_mode,
            filename_template=filename_template,
            templates=templates,
        )
    return generate_code_monofile(
        repo_dir=repo_dir,
        output_dir=output_dir,
        output_mode=output_mode,
        filename_template=filename_template,
        templates=templates,
    )
