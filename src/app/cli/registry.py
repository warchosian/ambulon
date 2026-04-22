"""Command registry for the Ambulon CLI dispatcher.

Each entry maps a CLI command name (what the user types after ``ambulon``) to
a ``(module_path, callable_name)`` pair. The referenced callable is expected to
follow the Ambulon convention::

    def main(argv: list[str] | None = None) -> int

and to work correctly when the process's ``sys.argv`` has been rewritten to
``[sys.argv[0], *cli_args_after_the_command_name]``. The dispatcher is
responsible for both tasks (see :mod:`app.cli.dispatch`).

Adding a new command is a one-line change here; there is no need to touch the
giant ``main()`` dispatcher anymore.
"""

from __future__ import annotations

from typing import Dict, Tuple

#: ``command_name -> (module_path, attribute_name)``.
#:
#: Only commands whose handler is a plain ``main(argv=None) -> int`` (or
#: equivalent no-argument ``main()``) belong here. Commands with bespoke
#: inline parsing still live in :mod:`app.cli.cli`.
STANDARD_COMMANDS: Dict[str, Tuple[str, str]] = {
    # Core tools
    "scan": ("app.scan.commands.scan", "main"),
    "ocr": ("app.ocr.commands.ocr", "main"),
    "mcp": ("app.mcp.commands.run_server", "main"),
    # Conversion
    "img2pdf": ("app.conversion", "img2pdf_main"),
    "compress-pdf": ("app.conversion", "compress_pdf_main"),
    "pdf2html": ("app.conversion", "pdf2html_main"),
    "pdf2md": ("app.conversion", "pdf2md_main"),
    # Encoding
    "check-utf8": ("app.encoding.commands.check_utf8", "main"),
    "fix-utf8": ("app.encoding.commands.fix_utf8", "main"),
    # WikiSI
    "wikisi-extract": ("app.wikisi.commands.wikisi_extract_json", "main"),
    "wikisi-md": ("app.wikisi.commands.wikisi_json_to_md", "main"),
    "wikisi-scrape": ("app.wikisi.commands.wikisi_scraper", "main"),
    "wikisi-sync-api": ("app.wikisi.commands.wikisi_sync_api", "main"),
    "wikisi-extract-apps": ("app.wikisi.commands.wikisi_extract_apps", "main"),

    # TOC
    "add-toc4html": ("app.toc.commands.add_toc4html", "main"),
    "add-toc4md": ("app.toc.commands.add_toc4md", "main"),
    "add-itoc4md": ("app.toc.commands.add_itoc4md", "main"),
    "check-toc4md": ("app.toc.commands.check_toc4md", "main"),
    "check-itoc4md": ("app.toc.commands.check_itoc4md", "main"),
    # Processing
    "concat-html": ("app.processing.commands.concat_html", "main"),
    "flatten-html": ("app.processing.commands.flatten_html", "main"),
    "flatten-md": ("app.processing.commands.flatten_md", "main"),
    "merge-html": ("app.processing.commands.merge_html", "main"),
    "merge-md": ("app.processing.commands.merge_md", "main"),
    "md2project": ("app.processing.commands.md2project", "main"),
    "project2md": ("app.processing.commands.project2md", "main"),
    "code2md": ("app.processing.commands.code2md", "main"),
    # VS Code extensions
    "vscode-install": ("app.vscode.commands.vscode_install", "main"),
    "vscode-uninstall": ("app.vscode.commands.vscode_uninstall", "main"),
    "vscode-list": ("app.vscode.commands.vscode_list", "main"),
    # Git hosting
    "github-release": ("app.github.commands.github_release", "main"),
    "gitlab-release": ("app.gitlab.releases.commands.gitlab_release", "main"),
    "gitlab-clone": ("app.gitlab.commands.gitlab_clone", "main"),
    "gitlab-monofile": ("app.gitlab.commands.gitlab_monofile", "main"),
    # Zip
    "zip-create": ("app.zip.commands.zip_create", "main"),
    "zip-extract": ("app.zip.commands.zip_extract", "main"),
    # LLM
    "llm": ("app.llm.commands.llm", "main"),
    "filter": ("app.llm.commands.filter", "main"),
    "summarize": ("app.llm.commands.summarize", "main"),
    "plantuml2mermaid": ("app.llm.commands.convert_plantuml_to_mermaid", "main"),
    "generate-docs": ("app.llm.commands.generate_docs", "main"),
    "migrate-ollama": ("app.llm.commands.migrate_ollama", "main"),
    # Diagrams
    "diagram2svg4md": ("app.diagrams.commands.diagram2svg4md", "main"),
    # CLI sub-modules
    "init": ("app.cli.commands.init", "handle_init_command"),
}


__all__ = ["STANDARD_COMMANDS"]
