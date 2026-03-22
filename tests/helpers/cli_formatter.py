"""
CLI Command Formatter for E2E Tests

This module provides utilities to format and display CLI commands
in a visually appealing way during end-to-end tests.
"""

from typing import List, Optional
import shutil


class CliCommandFormatter:
    """Formats CLI commands for visual display in tests."""

    # ANSI color codes for terminal output
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def format_command(
        command: str,
        args: List[str],
        description: Optional[str] = None,
        step_number: Optional[int] = None
    ) -> str:
        """
        Format a CLI command with visual enhancements.

        Args:
            command: The base command (e.g., 'ambulon piag-rag-search')
            args: List of arguments (e.g., ['--collection-id', '12345'])
            description: Optional description of what the command does
            step_number: Optional step number for the workflow

        Returns:
            Formatted string ready for printing
        """
        terminal_width = shutil.get_terminal_size((80, 20)).columns
        box_width = min(terminal_width - 4, 100)

        # Build the header
        lines = []
        lines.append("=" * box_width)

        if step_number:
            header = f"STEP {step_number}"
            if description:
                header += f": {description}"
            lines.append(f"{CliCommandFormatter.BOLD}{CliCommandFormatter.CYAN}{header}{CliCommandFormatter.RESET}")
        elif description:
            lines.append(f"{CliCommandFormatter.CYAN}{description}{CliCommandFormatter.RESET}")

        lines.append("-" * box_width)

        # Build the command line
        cmd_line = f"{CliCommandFormatter.GREEN}{command}{CliCommandFormatter.RESET}"

        # Format arguments with proper alignment
        if args:
            lines.append(f"{CliCommandFormatter.BOLD}Command:{CliCommandFormatter.RESET}")
            lines.append(f"  {cmd_line} \\")

            for i, arg in enumerate(args):
                is_last = (i == len(args) - 1)
                continuation = "" if is_last else " \\"

                # Highlight option names (starting with -)
                if arg.startswith('-'):
                    formatted_arg = f"{CliCommandFormatter.YELLOW}{arg}{CliCommandFormatter.RESET}"
                else:
                    formatted_arg = f"{CliCommandFormatter.BLUE}{arg}{CliCommandFormatter.RESET}"

                lines.append(f"    {formatted_arg}{continuation}")
        else:
            lines.append(f"{CliCommandFormatter.BOLD}Command:{CliCommandFormatter.RESET} {cmd_line}")

        lines.append("=" * box_width)

        return "\n".join(lines)

    @staticmethod
    def format_command_simple(command: str, args: List[str]) -> str:
        """
        Format a CLI command as a single line (for compact display).

        Args:
            command: The base command
            args: List of arguments

        Returns:
            Single-line formatted command
        """
        cmd_parts = [command] + args
        return f"{CliCommandFormatter.GREEN}$ {' '.join(cmd_parts)}{CliCommandFormatter.RESET}"

    @staticmethod
    def format_result(result: str, success: bool = True) -> str:
        """
        Format a command result/output.

        Args:
            result: The result text
            success: Whether the command succeeded

        Returns:
            Formatted result string
        """
        color = CliCommandFormatter.GREEN if success else '\033[91m'  # Red for failure
        status = "SUCCESS" if success else "FAILURE"

        lines = [
            f"{color}> Result: {status}{CliCommandFormatter.RESET}",
            result
        ]
        return "\n".join(lines)

    @staticmethod
    def print_command(
        command: str,
        args: List[str],
        description: Optional[str] = None,
        step_number: Optional[int] = None
    ) -> None:
        """
        Print a formatted CLI command to stdout.

        Args:
            command: The base command
            args: List of arguments
            description: Optional description
            step_number: Optional step number
        """
        formatted = CliCommandFormatter.format_command(
            command, args, description, step_number
        )
        print(f"\n{formatted}\n")


def build_piag_args(
    token: Optional[str] = None,
    project_id: Optional[str] = None,
    base_url: Optional[str] = None,
    collection: Optional[str] = None,
    collection_id: Optional[str] = None,
    document_id: Optional[str] = None,
    document_name: Optional[str] = None,
    **kwargs
) -> List[str]:
    """
    Build a list of arguments for PIAG commands.

    Args:
        token: API token
        project_id: Project ID
        base_url: Base URL for the API
        collection: Collection name
        collection_id: Collection ID
        document_id: Document ID
        document_name: Document name
        **kwargs: Additional key-value arguments

    Returns:
        List of command arguments
    """
    args = []

    if token:
        args.extend(["--token", token])
    if project_id:
        args.extend(["--project-id", project_id])
    if base_url:
        args.extend(["--base-url", base_url])
    if collection:
        args.extend(["--collection", collection])
    if collection_id:
        args.extend(["--collection-id", collection_id])
    if document_id:
        args.extend(["--document-id", document_id])
    if document_name:
        args.extend(["--document-name", document_name])

    # Add additional kwargs
    for key, value in kwargs.items():
        flag = f"--{key.replace('_', '-')}"
        args.extend([flag, str(value)])

    return args
