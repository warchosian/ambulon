import pytest
import os
import sys
import uuid
import time
from pathlib import Path
import json
import io

# Add the src directory to the sys.path to allow importing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from app.piag.core.config import load_config

# Import main functions from command scripts
from app.piag.commands.piag_collection_add import main as piag_collection_add_main
from app.piag.commands.piag_collection_get import main as piag_collection_get_main
from app.piag.commands.piag_collection_rm import main as piag_collection_rm_main
from app.piag.commands.piag_collection_update import main as piag_collection_update_main
from app.piag.commands.piag_doc_upload import main as piag_doc_upload_main
from app.piag.commands.piag_doc_list import main as piag_doc_list_main
from app.piag.commands.piag_doc_get import main as piag_doc_get_main
from app.piag.commands.piag_doc_chunks import main as piag_doc_chunks_main
from app.piag.commands.piag_doc_rm import main as piag_doc_rm_main
from app.piag.commands.piag_search import main as piag_search_main


# Configuration fixture
@pytest.fixture(scope="module")
def piag_config():
    # Attempt to load config from piag.yaml or environment variables
    config = load_config()

    api_token = os.getenv("PIAG_RAG_API_TOKEN") or config.get('security', {}).get('token')
    project_id = os.getenv("PIAG_RAG_PROJECT_ID") or config.get('project', {}).get('project_id')
    base_url = os.getenv("PIAG_RAG_BASE_URL") or config.get('api', {}).get('base_url')

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
    def __init__(self, main_func, default_args):
        self.main_func = main_func
        self.default_args = default_args

    def run(self, args):
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
        
        return returncode, stdout, stderr

@pytest.fixture(scope="module")
def cli_runner_factory(piag_config):
    def _runner(main_func):
        default_args = []
        if piag_config["api_token"]:
            default_args.extend(["--token", piag_config["api_token"]])
        if piag_config["project_id"]:
            default_args.extend(["--project-id", piag_config["project_id"]])
        if piag_config["base_url"]:
            default_args.extend(["--base-url", piag_config["base_url"]])
        return CliRunner(main_func, default_args)
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
    print(f"\n--- [Setup] Creating collection '{collection_name}' ---")
    
    runner = cli_runner_factory(piag_collection_add_main)
    returncode, stdout, stderr = runner.run(["--name", collection_name, "--description", "A temporary collection for e2e testing."])
    
    assert returncode == 0, f"Setup failed: Could not create collection. Stderr: {stderr}"
    
    try:
        # The output of piag_collection_add is not captured correctly, let's get it by name
        runner_get = cli_runner_factory(piag_collection_get_main)
        rc_get, so_get, se_get = runner_get.run(["--collection", collection_name])
        assert rc_get == 0, f"Setup failed: Could not retrieve created collection. Stderr: {se_get}"
        created_id = json.loads(so_get)['id']
        yield {"name": collection_name, "id": created_id}
    finally:
        print(f"\n--- [Teardown] Deleting collection '{collection_name}' ---")
        runner_rm = cli_runner_factory(piag_collection_rm_main)
        runner_rm.run(["--collection", collection_name, "--force"])

# End-to-end test for PIAG commands
@pytest.mark.integration
def test_piag_e2e_workflow(cli_runner_factory, created_collection, temp_document_file):
    collection_name = created_collection['name']
    collection_id = created_collection['id']
    updated_collection_description = f"Updated description for {collection_name}"
    document_file_path = str(temp_document_file)
    document_id = None

    # --- Step 1 & 2 are done by fixtures ---
    print(f"--- Testing with collection '{collection_name}' (ID: {collection_id}) ---")

    # --- Step 3: Update Collection by Name ---
    print(f"\n--- Updating collection '{collection_name}' description ---")
    runner = cli_runner_factory(piag_collection_update_main)
    returncode, stdout, stderr = runner.run(["--collection", collection_name, "--description", updated_collection_description])
    assert returncode == 0, f"Collection update failed: {stderr}"

    # --- Step 4: Verify Update by ID ---
    print(f"\n--- Verifying update for collection '{collection_id}' by ID ---")
    runner = cli_runner_factory(piag_collection_get_main)
    returncode, stdout, stderr = runner.run(["--collection", collection_id]) # Test by ID
    assert returncode == 0, f"Collection get by ID failed: {stderr}"
    get_result = json.loads(stdout)
    assert get_result['description'] == updated_collection_description
    print(f"Successfully verified updated description.")

    # --- Step 5: Upload Document ---
    print(f"\n--- Uploading document '{document_file_path}' to '{collection_name}' ---")
    time.sleep(1) # Give the API a moment
    runner = cli_runner_factory(piag_doc_upload_main)
    returncode, stdout, stderr = runner.run(["--collection", collection_name, "--file", document_file_path])
    assert returncode == 0, f"Document upload failed: {stderr}"
    upload_result = json.loads(stdout)
    document_id = upload_result['id']
    print(f"Uploaded document with ID: {document_id}")

    # --- Step 6: List Documents ---
    print(f"\n--- Listing documents in '{collection_name}' ---")
    time.sleep(2) # Wait for document to be indexed
    runner = cli_runner_factory(piag_doc_list_main)
    returncode, stdout, stderr = runner.run(["--collection", collection_name])
    assert returncode == 0, f"Document list failed: {stderr}"
    list_result = json.loads(stdout)
    assert any(doc['id'] == document_id for doc in list_result['items']), "Uploaded document not found in list."
    print(f"Successfully listed documents.")

    # --- Step 7: Get Document Chunks ---
    print(f"\n--- Getting chunks for document '{document_id}' ---")
    runner = cli_runner_factory(piag_doc_chunks_main)
    returncode, stdout, stderr = runner.run(["--collection", collection_name, "--document-id", document_id])
    assert returncode == 0, f"Get document chunks failed: {stderr}"
    chunks_result = json.loads(stdout)
    assert len(chunks_result.get('chunks', [])) > 0, "No chunks returned for document."
    print(f"Successfully retrieved document chunks.")

    # --- Step 8: Search Collection ---
    print(f"\n--- Searching collection '{collection_name}' ---")
    search_query = "xylophone"
    runner = cli_runner_factory(piag_search_main)
    returncode, stdout, stderr = runner.run(["--collection", collection_name, "--query", search_query])
    assert returncode == 0, f"Collection search failed: {stderr}"
    search_result = json.loads(stdout)
    assert len(search_result.get('chunks', [])) > 0, "Document not found in search results."
    print(f"Successfully found document in search results.")
    
    # --- Step 9: Get Document by ID ---
    print(f"\n--- Getting document '{document_id}' by ID ---")
    runner = cli_runner_factory(piag_doc_get_main)
    returncode, stdout, stderr = runner.run(["--collection", collection_name, "--document-id", document_id])
    assert returncode == 0, f"Get document by ID failed: {stderr}"
    get_doc_result = json.loads(stdout)
    assert get_doc_result['id'] == document_id, "Retrieved document ID mismatch."
    print(f"Successfully retrieved document by ID.")

    # --- Step 10: Delete Document ---
    print(f"\n--- Deleting document '{document_id}' ---")
    runner = cli_runner_factory(piag_doc_rm_main)
    returncode, stdout, stderr = runner.run(["--collection", collection_name, "--document-id", document_id, "--force"])
    assert returncode == 0, f"Document delete failed: {stderr}"
    print(f"Successfully deleted document.")

    # --- Step 11: Verify Document Deletion ---
    print(f"\n--- Verifying document '{document_id}' deletion ---")
    time.sleep(2) # Wait for deletion to be processed
    runner = cli_runner_factory(piag_doc_list_main)
    returncode, stdout, stderr = runner.run(["--collection", collection_name])
    assert returncode == 0, f"Document list failed after deletion check: {stderr}"
    list_result_after_delete = json.loads(stdout)
    assert not any(doc['id'] == document_id for doc in list_result_after_delete.get('items', [])), "Deleted document still found in list."
    print(f"Successfully verified document deletion.")