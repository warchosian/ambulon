import pytest
import os
import sys
import uuid
import time
from pathlib import Path
import json
import io

# Add the src directory to the sys.path to allow importing modules
# This line is removed as it's not needed with a poetry install
# sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from app.piag.core.config import load_config

# Import CLI formatter helpers
sys.path.insert(0, str(Path(__file__).parent.parent))
from helpers.cli_formatter import CliCommandFormatter, build_piag_args

# Import main functions from command scripts
from app.piag.commands.piag_rag_collection_add import main as piag_collection_add_main
from app.piag.commands.piag_rag_collection_get import main as piag_collection_get_main
from app.piag.commands.piag_rag_collection_rm import main as piag_collection_rm_main
from app.piag.commands.piag_rag_collection_update import main as piag_collection_update_main
from app.piag.commands.piag_rag_doc_upload import main as piag_doc_upload_main
from app.piag.commands.piag_rag_doc_list import main as piag_doc_list_main
from app.piag.commands.piag_rag_doc_get import main as piag_doc_get_main
from app.piag.commands.piag_rag_doc_chunks import main as piag_doc_chunks_main
from app.piag.commands.piag_rag_doc_rm import main as piag_doc_rm_main
from app.piag.commands.piag_rag_search import main as piag_search_main


# Configuration fixture
@pytest.fixture(scope="module")
def piag_config():
    # Attempt to load config from piag.yaml or environment variables
    config = load_config()

    api_token = os.getenv("PIAG_RAG_API_TOKEN") or config.get('piag', {}).get('rag', {}).get('security', {}).get('token')
    project_id = os.getenv("PIAG_RAG_PROJECT_ID") or config.get('piag', {}).get('rag', {}).get('project', {}).get('project_id')
    base_url = os.getenv("PIAG_RAG_BASE_URL") or config.get('piag', {}).get('rag', {}).get('api', {}).get('base_url')

    if not api_token or not project_id:
        pytest.skip("PIAG_RAG_API_TOKEN and PIAG_RAG_PROJECT_ID environment variables or a valid config file must be set.")

    yield {
        "api_token": api_token,
        "project_id": project_id,
        "base_url": base_url,
        "config": config
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
                print(CliCommandFormatter.format_result(f"Command failed with code {returncode}\n{stderr}", success=False))

        return returncode, stdout, stderr

@pytest.fixture(scope="module")
def cli_runner_factory(piag_config):
    def _runner(main_func, command_name="piag-command"):
        default_args = []
        if piag_config["api_token"]:
            default_args.extend(["--token", piag_config["api_token"]])
        if piag_config["project_id"]:
            default_args.extend(["--project-id", piag_config["project_id"]])
        if piag_config["base_url"]:
            default_args.extend(["--base-url", piag_config["base_url"]])
        return CliRunner(main_func, default_args, command_name)
    return _runner


@pytest.fixture(scope="module")
def temp_document_file():
    file_content = "This is a test document for PIAG RAG API integration testing. It contains a unique keyword: xylophone."
    file_path = Path(f"temp_test_document_{uuid.uuid4().hex[:8]}.txt")
    file_path.write_text(file_content)
    yield file_path
    if file_path.exists():
        os.remove(file_path)

# --- Test Fixture for Collection ---
@pytest.fixture(scope="module")
def created_collection(cli_runner_factory):
    unique_id = uuid.uuid4().hex[:8]
    collection_name = f"test-collection-{unique_id}"
    print(f"\n{'='*80}")
    print(f"{'='*80}")
    print(f"SETUP: Creating test collection")
    print(f"{'='*80}")

    runner = cli_runner_factory(piag_collection_add_main, "piag-rag-collection-add")
    returncode, stdout, stderr = runner.run(
        ["--name", collection_name, "--description", "A temporary collection for e2e testing."],
        description="Create a test collection for E2E workflow",
        step_number=0
    )

    assert returncode == 0, f"Setup failed: Could not create collection. Stderr: {stderr}"

    try:
        # The output of piag_collection_add is not captured correctly, let's get it by name
        runner_get = cli_runner_factory(piag_collection_get_main, "piag-rag-collection-get")
        rc_get, so_get, se_get = runner_get.run(
            ["--collection", collection_name],
            description="Retrieve created collection to get its ID",
            show_command=False  # Don't show this internal step
        )
        assert rc_get == 0, f"Setup failed: Could not retrieve created collection. Stderr: {se_get}"
        created_id = json.loads(so_get)['id']
        print(f"\nCollection created: {collection_name} (ID: {created_id})\n")
        yield {"name": collection_name, "id": created_id}
    finally:
        print(f"\n{'='*80}")
        print(f"TEARDOWN: Cleaning up test collection")
        print(f"{'='*80}")
        runner_rm = cli_runner_factory(piag_collection_rm_main, "piag-rag-collection-rm")
        runner_rm.run(
            ["--collection", collection_name, "--force"],
            description="Delete the test collection",
            show_command=True
        )

# End-to-end test for PIAG commands
@pytest.mark.integration
def test_piag_e2e_workflow(cli_runner_factory, created_collection, temp_document_file):
    collection_name = created_collection['name']
    collection_id = created_collection['id']
    updated_collection_description = f"Updated description for {collection_name}"
    document_file_path = str(temp_document_file)
    document_id = None

    # --- Step 1 & 2 are done by fixtures ---
    print(f"\n{'='*80}")
    print(f"STARTING E2E WORKFLOW TEST")
    print(f"Collection: {collection_name} (ID: {collection_id})")
    print(f"{'='*80}\n")

    # --- Step 1: Update Collection by Name ---
    runner = cli_runner_factory(piag_collection_update_main, "piag-rag-collection-update")
    returncode, stdout, stderr = runner.run(
        ["--collection", collection_name, "--description", updated_collection_description],
        description="Update collection description by name",
        step_number=1
    )
    assert returncode == 0, f"Collection update failed: {stderr}"

    # --- Step 2: Verify Update by ID ---
    runner = cli_runner_factory(piag_collection_get_main, "piag-rag-collection-get")
    returncode, stdout, stderr = runner.run(
        ["--collection", collection_id],
        description="Verify collection update by ID",
        step_number=2
    )
    assert returncode == 0, f"Collection get by ID failed: {stderr}"
    get_result = json.loads(stdout)
    assert get_result['description'] == updated_collection_description
    print(f"✓ Successfully verified updated description.\n")

    # --- Step 3: Upload Document ---
    time.sleep(1)  # Give the API a moment
    runner = cli_runner_factory(piag_doc_upload_main, "piag-rag-doc-upload")
    returncode, stdout, stderr = runner.run(
        ["--collection", collection_name, "--file", document_file_path],
        description="Upload document to collection",
        step_number=3
    )
    assert returncode == 0, f"Document upload failed: {stderr}"
    upload_result = json.loads(stdout)
    document_id = upload_result['id']
    print(f"✓ Uploaded document with ID: {document_id}\n")

    # --- Step 4: List Documents ---
    time.sleep(2)  # Wait for document to be indexed
    runner = cli_runner_factory(piag_doc_list_main, "piag-rag-doc-list")
    returncode, stdout, stderr = runner.run(
        ["--collection", collection_name],
        description="List all documents in collection",
        step_number=4
    )
    assert returncode == 0, f"Document list failed: {stderr}"
    list_result = json.loads(stdout)
    assert any(doc['id'] == document_id for doc in list_result['items']), "Uploaded document not found in list."
    print(f"✓ Found {len(list_result['items'])} document(s) in collection.\n")

    # --- Step 5: Get Document Chunks ---
    runner = cli_runner_factory(piag_doc_chunks_main, "piag-rag-doc-chunks")
    returncode, stdout, stderr = runner.run(
        ["--collection", collection_name, "--document-id", document_id],
        description="Retrieve chunks from document",
        step_number=5
    )
    assert returncode == 0, f"Get document chunks failed: {stderr}"
    chunks_result = json.loads(stdout)
    assert len(chunks_result.get('chunks', [])) > 0, "No chunks returned for document."
    print(f"✓ Successfully retrieved {len(chunks_result.get('chunks', []))} chunk(s).\n")

    # --- Step 6: Search Collection ---
    search_query = "xylophone"
    runner = cli_runner_factory(piag_search_main, "piag-rag-search")
    returncode, stdout, stderr = runner.run(
        ["--collection", collection_name, "--query", search_query],
        description="Search for relevant chunks in collection",
        step_number=6
    )
    assert returncode == 0, f"Collection search failed: {stderr}"
    search_result = json.loads(stdout)
    assert len(search_result.get('chunks', [])) > 0, "Document not found in search results."
    print(f"✓ Found {len(search_result.get('chunks', []))} relevant chunk(s) for query '{search_query}'.\n")

    # --- Step 7: Get Document by ID ---
    runner = cli_runner_factory(piag_doc_get_main, "piag-rag-doc-get")
    returncode, stdout, stderr = runner.run(
        ["--collection", collection_name, "--document-id", document_id],
        description="Get document metadata by ID",
        step_number=7
    )
    assert returncode == 0, f"Get document by ID failed: {stderr}"
    get_doc_result = json.loads(stdout)
    assert get_doc_result['id'] == document_id, "Retrieved document ID mismatch."
    print(f"✓ Successfully retrieved document metadata.\n")

    # --- Step 8: Delete Document ---
    runner = cli_runner_factory(piag_doc_rm_main, "piag-rag-doc-rm")
    returncode, stdout, stderr = runner.run(
        ["--collection", collection_name, "--document-id", document_id, "--force"],
        description="Delete document from collection",
        step_number=8
    )
    assert returncode == 0, f"Document delete failed: {stderr}"
    print(f"✓ Successfully deleted document.\n")

    # --- Step 9: Verify Document Deletion ---
    time.sleep(2)  # Wait for deletion to be processed
    runner = cli_runner_factory(piag_doc_list_main, "piag-rag-doc-list")
    returncode, stdout, stderr = runner.run(
        ["--collection", collection_name],
        description="Verify document was deleted",
        step_number=9
    )
    assert returncode == 0, f"Document list failed after deletion check: {stderr}"
    list_result_after_delete = json.loads(stdout)
    assert not any(doc['id'] == document_id for doc in list_result_after_delete.get('items', [])), "Deleted document still found in list."
    print(f"✓ Successfully verified document deletion.\n")

    print(f"{'='*80}")
    print(f"E2E WORKFLOW TEST COMPLETED SUCCESSFULLY")
    print(f"{'='*80}\n")