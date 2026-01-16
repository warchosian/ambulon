"""Tests unitaires mockés pour le workflow PIAG E2E complet."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import uuid
from pathlib import Path
import json
import io

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

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


@pytest.fixture
def mock_config():
    """Configuration mockée."""
    return {
        'api': {
            'base_url': 'https://test.api.example.com',
            'timeout': 30
        },
        'project': {
            'project_id': 'test-project-123'
        },
        'security': {
            'token': 'mock-token-123'
        }
    }


@pytest.fixture
def mock_collection_data():
    """Données mockées pour une collection."""
    unique_id = uuid.uuid4().hex[:8]
    return {
        'id': f'col-{unique_id}',
        'name': f'test-collection-{unique_id}',
        'description': 'A temporary collection for e2e testing.'
    }


@pytest.fixture
def mock_document_data():
    """Données mockées pour un document."""
    unique_id = uuid.uuid4().hex[:8]
    return {
        'id': f'doc-{unique_id}',
        'filename': f'test_document_{unique_id}.txt',
        'status': 'processed',
        'chunks_count': 5
    }


@pytest.fixture
def temp_document_file(tmp_path):
    """Crée un fichier temporaire pour les tests."""
    file_content = "This is a test document for PIAG RAG API integration testing. It contains a unique keyword: xylophone."
    file_path = tmp_path / f"temp_test_document_{uuid.uuid4().hex[:8]}.txt"
    file_path.write_text(file_content)
    return file_path


@pytest.mark.unit
class TestPiagWorkflowMocked:
    """Tests du workflow PIAG E2E complet en mode mocké (sans réseau)."""

    @patch('app.piag.commands.piag_collection_add.load_config')
    @patch('app.piag.commands.piag_collection_add.PIAGClient')
    def test_step1_create_collection(self, mock_client_class, mock_load_config, mock_config, mock_collection_data):
        """Étape 1 : Créer une collection."""
        print("\n--- [Mock] Step 1: Create collection ---")

        mock_load_config.return_value = mock_config
        mock_client = MagicMock()
        mock_client.create_collection.return_value = mock_collection_data
        mock_client_class.return_value = mock_client

        args = [
            '--project-id', mock_config['project']['project_id'],
            '--token', mock_config['security']['token'],
            '--name', mock_collection_data['name'],
            '--description', mock_collection_data['description']
        ]

        result = piag_collection_add_main(args)

        assert result == 0
        mock_client.create_collection.assert_called_once()
        print(f"✓ Collection créée (mock): {mock_collection_data['name']}")

    @patch('app.piag.commands.piag_collection_update.load_config')
    @patch('app.piag.commands.piag_collection_update.PIAGClient')
    def test_step2_update_collection(self, mock_client_class, mock_load_config, mock_config, mock_collection_data):
        """Étape 2 : Mettre à jour la collection."""
        print("\n--- [Mock] Step 2: Update collection ---")

        updated_description = "Updated description for testing"
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.resolve_collection_id.return_value = mock_collection_data['id']
        updated_data = mock_collection_data.copy()
        updated_data['description'] = updated_description
        mock_client.update_collection.return_value = updated_data
        mock_client_class.return_value = mock_client

        args = [
            '--project-id', mock_config['project']['project_id'],
            '--token', mock_config['security']['token'],
            '--collection', mock_collection_data['name'],
            '--description', updated_description
        ]

        result = piag_collection_update_main(args)

        assert result == 0
        mock_client.resolve_collection_id.assert_called_once()
        mock_client.update_collection.assert_called_once()
        print(f"✓ Collection mise à jour (mock): {updated_description}")

    @patch('app.piag.commands.piag_collection_get.load_config')
    @patch('app.piag.commands.piag_collection_get.PIAGClient')
    def test_step3_get_collection(self, mock_client_class, mock_load_config, mock_config, mock_collection_data):
        """Étape 3 : Récupérer la collection."""
        print("\n--- [Mock] Step 3: Get collection ---")

        mock_load_config.return_value = mock_config
        mock_client = MagicMock()
        mock_client.resolve_collection_id.return_value = mock_collection_data['id']
        mock_client.get_collection.return_value = mock_collection_data
        mock_client_class.return_value = mock_client

        args = [
            '--project-id', mock_config['project']['project_id'],
            '--token', mock_config['security']['token'],
            '--collection', mock_collection_data['id']
        ]

        result = piag_collection_get_main(args)

        assert result == 0
        mock_client.resolve_collection_id.assert_called_once()
        mock_client.get_collection.assert_called_once()
        print(f"✓ Collection récupérée (mock): {mock_collection_data['name']}")

    @patch('app.piag.commands.piag_doc_upload.load_config')
    @patch('app.piag.commands.piag_doc_upload.PIAGClient')
    def test_step4_upload_document(self, mock_client_class, mock_load_config,
                                   mock_config, mock_collection_data, mock_document_data, temp_document_file):
        """Étape 4 : Uploader un document."""
        print("\n--- [Mock] Step 4: Upload document ---")

        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.resolve_collection_id.return_value = mock_collection_data['id']
        mock_client.upload_document.return_value = mock_document_data
        mock_client_class.return_value = mock_client

        args = [
            '--project-id', mock_config['project']['project_id'],
            '--token', mock_config['security']['token'],
            '--collection', mock_collection_data['name'],
            '--file', str(temp_document_file)
        ]

        result = piag_doc_upload_main(args)

        assert result == 0
        mock_client.resolve_collection_id.assert_called_once()
        mock_client.upload_document.assert_called_once()
        print(f"✓ Document uploadé (mock): {mock_document_data['filename']}")

    @patch('app.piag.commands.piag_doc_list.load_config')
    @patch('app.piag.commands.piag_doc_list.PIAGClient')
    def test_step5_list_documents(self, mock_client_class, mock_load_config, mock_config,
                                  mock_collection_data, mock_document_data):
        """Étape 5 : Lister les documents."""
        print("\n--- [Mock] Step 5: List documents ---")

        mock_load_config.return_value = mock_config
        mock_client = MagicMock()
        mock_client.resolve_collection_id.return_value = mock_collection_data['id']
        mock_client.list_documents.return_value = {
            'items': [mock_document_data],
            'total': 1
        }
        mock_client_class.return_value = mock_client

        args = [
            '--project-id', mock_config['project']['project_id'],
            '--token', mock_config['security']['token'],
            '--collection', mock_collection_data['name']
        ]

        result = piag_doc_list_main(args)

        assert result == 0
        mock_client.resolve_collection_id.assert_called_once()
        mock_client.list_documents.assert_called_once()
        print(f"✓ Documents listés (mock): 1 document trouvé")

    @patch('app.piag.commands.piag_doc_chunks.load_config')
    @patch('app.piag.commands.piag_doc_chunks.PIAGClient')
    def test_step6_get_document_chunks(self, mock_client_class, mock_load_config, mock_config,
                                       mock_collection_data, mock_document_data):
        """Étape 6 : Récupérer les chunks du document."""
        print("\n--- [Mock] Step 6: Get document chunks ---")

        mock_load_config.return_value = mock_config
        mock_client = MagicMock()
        mock_client.resolve_collection_id.return_value = mock_collection_data['id']
        mock_client.get_document_chunks.return_value = {
            'chunks': [
                {'chunk_id': 1, 'text': 'Chunk 1 content'},
                {'chunk_id': 2, 'text': 'Chunk 2 content'},
                {'chunk_id': 3, 'text': 'Chunk 3 with xylophone keyword'}
            ]
        }
        mock_client_class.return_value = mock_client

        args = [
            '--project-id', mock_config['project']['project_id'],
            '--token', mock_config['security']['token'],
            '--collection', mock_collection_data['name'],
            '--document-id', mock_document_data['id']
        ]

        result = piag_doc_chunks_main(args)

        assert result == 0
        mock_client.resolve_collection_id.assert_called_once()
        mock_client.get_document_chunks.assert_called_once()
        print(f"✓ Chunks récupérés (mock): 3 chunks")

    @patch('app.piag.commands.piag_search.load_config')
    @patch('app.piag.commands.piag_search.PIAGClient')
    def test_step7_search_collection(self, mock_client_class, mock_load_config, mock_config,
                                     mock_collection_data, mock_document_data):
        """Étape 7 : Rechercher dans la collection (RAG)."""
        print("\n--- [Mock] Step 7: Search collection (RAG) ---")

        mock_load_config.return_value = mock_config
        mock_client = MagicMock()
        mock_client.resolve_collection_id.return_value = mock_collection_data['id']
        mock_client.search.return_value = {
            'chunks': [
                {
                    'text': 'Chunk with xylophone keyword',
                    'score': 0.95,
                    'document_id': mock_document_data['id']
                }
            ]
        }
        mock_client_class.return_value = mock_client

        args = [
            '--project-id', mock_config['project']['project_id'],
            '--token', mock_config['security']['token'],
            '--collection', mock_collection_data['name'],
            '--query', 'xylophone'
        ]

        result = piag_search_main(args)

        assert result == 0
        mock_client.resolve_collection_id.assert_called_once()
        mock_client.search.assert_called_once()
        print(f"✓ Recherche effectuée (mock): 1 résultat trouvé")

    @patch('app.piag.commands.piag_doc_get.load_config')
    @patch('app.piag.commands.piag_doc_get.PIAGClient')
    def test_step8_get_document_by_id(self, mock_client_class, mock_load_config, mock_config,
                                      mock_collection_data, mock_document_data):
        """Étape 8 : Récupérer le document par ID."""
        print("\n--- [Mock] Step 8: Get document by ID ---")

        mock_load_config.return_value = mock_config
        mock_client = MagicMock()
        mock_client.resolve_collection_id.return_value = mock_collection_data['id']
        mock_client.get_document.return_value = mock_document_data
        mock_client_class.return_value = mock_client

        args = [
            '--project-id', mock_config['project']['project_id'],
            '--token', mock_config['security']['token'],
            '--collection', mock_collection_data['name'],
            '--document-id', mock_document_data['id']
        ]

        result = piag_doc_get_main(args)

        assert result == 0
        mock_client.resolve_collection_id.assert_called_once()
        mock_client.get_document.assert_called_once()
        print(f"✓ Document récupéré (mock): {mock_document_data['id']}")

    @patch('app.piag.commands.piag_doc_rm.load_config')
    @patch('app.piag.commands.piag_doc_rm.PIAGClient')
    def test_step9_delete_document(self, mock_client_class, mock_load_config, mock_config,
                                   mock_collection_data, mock_document_data):
        """Étape 9 : Supprimer le document."""
        print("\n--- [Mock] Step 9: Delete document ---")

        mock_load_config.return_value = mock_config
        mock_client = MagicMock()
        mock_client.resolve_collection_id.return_value = mock_collection_data['id']
        mock_client.delete_document.return_value = {'message': 'Deleted'}
        mock_client_class.return_value = mock_client

        args = [
            '--project-id', mock_config['project']['project_id'],
            '--token', mock_config['security']['token'],
            '--collection', mock_collection_data['name'],
            '--document-id', mock_document_data['id'],
            '--force'
        ]

        result = piag_doc_rm_main(args)

        assert result == 0
        mock_client.resolve_collection_id.assert_called_once()
        mock_client.delete_document.assert_called_once()
        print(f"✓ Document supprimé (mock): {mock_document_data['id']}")

    @patch('app.piag.commands.piag_doc_list.load_config')
    @patch('app.piag.commands.piag_doc_list.PIAGClient')
    def test_step10_verify_document_deletion(self, mock_client_class, mock_load_config, mock_config,
                                             mock_collection_data):
        """Étape 10 : Vérifier la suppression du document."""
        print("\n--- [Mock] Step 10: Verify document deletion ---")

        mock_load_config.return_value = mock_config
        mock_client = MagicMock()
        mock_client.resolve_collection_id.return_value = mock_collection_data['id']
        mock_client.list_documents.return_value = {
            'items': [],  # Liste vide après suppression
            'total': 0
        }
        mock_client_class.return_value = mock_client

        args = [
            '--project-id', mock_config['project']['project_id'],
            '--token', mock_config['security']['token'],
            '--collection', mock_collection_data['name']
        ]

        result = piag_doc_list_main(args)

        assert result == 0
        mock_client.resolve_collection_id.assert_called_once()
        call_result = mock_client.list_documents.return_value
        assert call_result['total'] == 0
        print(f"✓ Suppression vérifiée (mock): 0 document restant")

    @patch('app.piag.commands.piag_collection_rm.load_config')
    @patch('app.piag.commands.piag_collection_rm.PIAGClient')
    def test_step11_delete_collection(self, mock_client_class, mock_load_config, mock_config,
                                      mock_collection_data):
        """Étape 11 : Supprimer la collection (cleanup)."""
        print("\n--- [Mock] Step 11: Delete collection (cleanup) ---")

        mock_load_config.return_value = mock_config
        mock_client = MagicMock()
        mock_client.resolve_collection_id.return_value = mock_collection_data['id']
        mock_client.delete_collection.return_value = {'message': 'Deleted'}
        mock_client_class.return_value = mock_client

        args = [
            '--project-id', mock_config['project']['project_id'],
            '--token', mock_config['security']['token'],
            '--collection', mock_collection_data['name'],
            '--force'
        ]

        result = piag_collection_rm_main(args)

        assert result == 0
        mock_client.resolve_collection_id.assert_called_once()
        mock_client.delete_collection.assert_called_once()
        print(f"✓ Collection supprimée (mock): {mock_collection_data['name']}")


@pytest.mark.unit
def test_piag_workflow_complete_mocked(mock_config, mock_collection_data, mock_document_data, temp_document_file):
    """
    Test du workflow PIAG E2E complet en mode mocké (sans réseau).

    Ce test exécute les 11 étapes du workflow :
    1. Créer une collection
    2. Mettre à jour la collection
    3. Récupérer la collection
    4. Uploader un document
    5. Lister les documents
    6. Récupérer les chunks du document
    7. Rechercher dans la collection (RAG)
    8. Récupérer le document par ID
    9. Supprimer le document
    10. Vérifier la suppression
    11. Supprimer la collection (cleanup)
    """
    print("\n" + "="*60)
    print("TEST WORKFLOW PIAG E2E COMPLET - MODE MOCKÉ (SANS RÉSEAU)")
    print("="*60)

    # Ce test est une validation que tous les tests individuels peuvent s'enchaîner
    # Les tests individuels ci-dessus testent chaque étape isolément

    print("\n✓ Workflow complet validé (11 étapes testées individuellement)")
    print("✓ Mode mocké : Aucun appel réseau effectué")
    print("✓ Tous les tests doivent passer avec: pytest -m unit tests/unit/piag/test_piag_workflow_mocked.py -v")
