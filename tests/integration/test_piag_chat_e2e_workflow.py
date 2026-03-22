"""
End-to-end tests for PIAG Chat commands with visual command display.

This test suite demonstrates the complete PIAG Chat workflow:
1. Check API key info
2. Simple query without context
3. Query with RAG context (chunks from file)
4. Query with automatic chunk retrieval from PIAG RAG
5. Legacy completion endpoint

All commands are displayed visually with their full arguments.
"""

import pytest
import os
import sys
import uuid
import json
import io
from pathlib import Path

# Import CLI formatter helpers
sys.path.insert(0, str(Path(__file__).parent.parent))
from helpers.cli_formatter import CliCommandFormatter

# Import main functions from command scripts
from app.piag.commands.piag_chat_apikey_info import main as piag_chat_apikey_info_main
from app.piag.commands.piag_chat_basic_query import main as piag_chat_basic_query_main
from app.piag.commands.piag_chat_query import main as piag_chat_query_main
from app.piag.commands.piag_chat_completion import main as piag_chat_completion_main


# Configuration fixture
@pytest.fixture(scope="module")
def piag_chat_config():
    """Load PIAG Chat configuration from environment or config file."""
    chat_token = os.getenv("PIAG_CHAT_API_TOKEN")
    api_url = os.getenv("PIAG_CHAT_API_URL", "https://preprod.api.piag.e2.rie.gouv.fr/v1")

    if not chat_token:
        pytest.skip("PIAG_CHAT_API_TOKEN environment variable must be set.")

    yield {
        "chat_token": chat_token,
        "api_url": api_url,
    }


# Helper to run CLI commands and capture output
class CliRunner:
    def __init__(self, main_func, default_args, command_name):
        self.main_func = main_func
        self.default_args = default_args
        self.command_name = command_name

    def run(self, args, description=None, step_number=None, show_command=True):
        """
        Run a CLI command and capture output.

        Args:
            args: Command arguments
            description: Description of what the command does
            step_number: Step number in the workflow
            show_command: Whether to display the command visually

        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        # Display the command if requested
        if show_command:
            full_command = f"ambulon {self.command_name}"
            all_args = self.default_args + args
            CliCommandFormatter.print_command(
                full_command,
                all_args,
                description,
                step_number
            )

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = capture_stdout = io.StringIO()
        sys.stderr = capture_stderr = io.StringIO()

        returncode = -1
        try:
            full_args = self.default_args + args
            returncode = self.main_func(full_args)
            stdout = capture_stdout.getvalue()
            stderr = capture_stderr.getvalue()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        # Display result
        if show_command:
            if returncode == 0:
                print(CliCommandFormatter.format_result("Command executed successfully", success=True))
            else:
                print(CliCommandFormatter.format_result(
                    f"Command failed with code {returncode}\n{stderr}",
                    success=False
                ))

        return returncode, stdout, stderr


@pytest.fixture(scope="module")
def cli_runner_factory(piag_chat_config):
    """Factory to create CliRunner instances with default chat config."""
    def _runner(main_func, command_name="piag-chat-command"):
        default_args = []
        if piag_chat_config["chat_token"]:
            default_args.extend(["--chat-token", piag_chat_config["chat_token"]])
        if piag_chat_config["api_url"]:
            default_args.extend(["--api-url", piag_chat_config["api_url"]])
        return CliRunner(main_func, default_args, command_name)
    return _runner


@pytest.fixture(scope="module")
def sample_chunks_file(tmp_path_factory):
    """Create a temporary file with sample chunks for testing."""
    chunks_data = {
        "chunks": [
            {
                "content": "La procédure de déploiement se déroule en 3 étapes principales: "
                          "1) Préparation de l'environnement, 2) Build de l'application, "
                          "3) Déploiement sur le serveur de production.",
                "metadata": {"source": "manuel_deploiement.pdf", "page": 12}
            },
            {
                "content": "Avant tout déploiement, il est impératif de vérifier que tous les "
                          "tests unitaires et d'intégration passent avec succès.",
                "metadata": {"source": "manuel_deploiement.pdf", "page": 13}
            },
            {
                "content": "Le serveur de production est accessible via SSH sur le port 22. "
                          "Les credentials sont stockés dans le gestionnaire de secrets.",
                "metadata": {"source": "manuel_deploiement.pdf", "page": 14}
            }
        ]
    }

    temp_dir = tmp_path_factory.mktemp("test_chunks")
    chunks_file = temp_dir / "sample_chunks.json"
    chunks_file.write_text(json.dumps(chunks_data, indent=2, ensure_ascii=False))

    yield str(chunks_file)


# End-to-end test for PIAG Chat commands
@pytest.mark.integration
def test_piag_chat_e2e_workflow(cli_runner_factory, sample_chunks_file):
    """
    Test the complete PIAG Chat workflow with visual command display.
    """
    print(f"\n{'='*80}")
    print(f"{'='*80}")
    print(f"STARTING PIAG CHAT E2E WORKFLOW TEST")
    print(f"{'='*80}\n")

    # --- Step 1: Check API Key Info ---
    runner = cli_runner_factory(piag_chat_apikey_info_main, "piag-chat-apikey-info")
    returncode, stdout, stderr = runner.run(
        [],
        description="Check API key budget and usage information",
        step_number=1
    )
    # Note: This might fail if the token doesn't support this endpoint, so we don't assert
    if returncode == 0:
        print(f"✓ Successfully retrieved API key info.\n")
    else:
        print(f"⚠ API key info endpoint not available or failed.\n")

    # --- Step 2: Simple Query (No Context) ---
    runner = cli_runner_factory(piag_chat_basic_query_main, "piag-chat-basic-query")
    returncode, stdout, stderr = runner.run(
        ["--question", "Quelle est la capitale de la France ?"],
        description="Ask a simple question without any context",
        step_number=2
    )
    assert returncode == 0, f"Basic query failed: {stderr}"
    print(f"✓ Response preview: {stdout[:200]}...\n")

    # --- Step 3: Query with System Message ---
    runner = cli_runner_factory(piag_chat_basic_query_main, "piag-chat-basic-query")
    returncode, stdout, stderr = runner.run(
        [
            "--question", "Bonjour",
            "--system", "Tu es un assistant technique spécialisé en DevOps."
        ],
        description="Query with a custom system message",
        step_number=3
    )
    assert returncode == 0, f"Query with system message failed: {stderr}"
    print(f"✓ Response received with custom system prompt.\n")

    # --- Step 4: Query with RAG Context (from file) ---
    runner = cli_runner_factory(piag_chat_query_main, "piag-chat-query")
    returncode, stdout, stderr = runner.run(
        [
            "--question", "Quelle est la procédure de déploiement ?",
            "--chunks", sample_chunks_file
        ],
        description="Ask a question with RAG context from a chunks file",
        step_number=4
    )
    assert returncode == 0, f"RAG query failed: {stderr}"
    print(f"✓ Response generated using RAG context.\n")
    print(f"  Response preview: {stdout[:300]}...\n")

    # --- Step 5: Query with Output File ---
    output_file = Path(sample_chunks_file).parent / "chat_response.md"
    runner = cli_runner_factory(piag_chat_query_main, "piag-chat-query")
    returncode, stdout, stderr = runner.run(
        [
            "--question", "Résume la procédure de déploiement en 3 points",
            "--chunks", sample_chunks_file,
            "--output", str(output_file)
        ],
        description="Generate response and save to markdown file",
        step_number=5
    )
    assert returncode == 0, f"Query with output file failed: {stderr}"
    assert output_file.exists(), "Output file was not created"
    print(f"✓ Response saved to: {output_file}\n")

    # --- Step 6: Legacy Completion Endpoint ---
    runner = cli_runner_factory(piag_chat_completion_main, "piag-chat-completion")
    returncode, stdout, stderr = runner.run(
        [
            "--prompt", "Explique en une phrase ce qu'est le DevOps:",
            "--max-tokens", "50"
        ],
        description="Use legacy completion endpoint (prompt/completion format)",
        step_number=6
    )
    # Note: This might not be supported, so we don't assert
    if returncode == 0:
        print(f"✓ Legacy completion endpoint works.\n")
        print(f"  Completion: {stdout[:200]}...\n")
    else:
        print(f"⚠ Legacy completion endpoint not available or failed.\n")

    print(f"{'='*80}")
    print(f"PIAG CHAT E2E WORKFLOW TEST COMPLETED")
    print(f"{'='*80}\n")


@pytest.mark.integration
def test_piag_chat_rag_integration(cli_runner_factory, sample_chunks_file):
    """
    Test RAG integration: showing how to combine PIAG RAG search with PIAG Chat.

    This test demonstrates the typical workflow:
    1. Search for relevant chunks (simulated with pre-made file)
    2. Ask a question using those chunks
    3. Get a context-aware response
    """
    print(f"\n{'='*80}")
    print(f"RAG + CHAT INTEGRATION WORKFLOW")
    print(f"{'='*80}\n")

    print("This workflow demonstrates how to use PIAG RAG search results with PIAG Chat:")
    print("")
    print("  [Previous step - would be done with piag-rag-search]")
    print("  $ ambulon piag-rag-search \\")
    print("      --collection-id <ID> \\")
    print("      --query 'procédure déploiement' \\")
    print("      --json > chunks.json")
    print("")

    # --- Now use those chunks with Chat ---
    runner = cli_runner_factory(piag_chat_query_main, "piag-chat-query")
    returncode, stdout, stderr = runner.run(
        [
            "--question", "Quelles sont les 3 étapes principales de déploiement ?",
            "--chunks", sample_chunks_file
        ],
        description="Use PIAG Chat with chunks from PIAG RAG search",
        step_number=1
    )
    assert returncode == 0, f"RAG+Chat integration failed: {stderr}"

    # Parse the response to check it's relevant
    assert "déploiement" in stdout.lower() or "étape" in stdout.lower(), \
        "Response doesn't seem to use the context"

    print(f"✓ Successfully generated context-aware response.\n")
    print(f"Response:\n{'-'*80}")
    print(stdout[:500])
    print(f"{'-'*80}\n")

    print(f"{'='*80}")
    print(f"RAG + CHAT INTEGRATION TEST COMPLETED")
    print(f"{'='*80}\n")
