"""Tests unitaires mockés pour PIAGClient."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from app.piag.core.client import PIAGClient


@pytest.fixture
def mock_config():
    """Configuration mockée."""
    return {
        'api': {
            'base_url': 'https://test.api.example.com',
            'timeout': 30
        },
        'logging': {
            'log_requests': False,
            'log_responses': False
        }
    }


@pytest.fixture
def piag_client(mock_config):
    """Fixture client PIAG."""
    return PIAGClient(api_token='test-token-123', config=mock_config)


@pytest.mark.unit
class TestPIAGClientInit:
    """Tests d'initialisation du client."""

    def test_init_with_config(self, mock_config):
        """Test initialisation avec config."""
        client = PIAGClient(api_token='token', config=mock_config)

        assert client.api_token == 'token'
        assert client.base_url == 'https://test.api.example.com'
        assert client.timeout == 30

    def test_init_with_custom_base_url(self, mock_config):
        """Test avec URL personnalisée (priorité sur config)."""
        client = PIAGClient(
            api_token='token',
            base_url='https://custom.api.com',
            config=mock_config
        )

        assert client.base_url == 'https://custom.api.com'

    def test_init_without_config(self):
        """Test sans configuration."""
        with patch('app.piag.core.client.get_config') as mock_get_config:
            mock_get_config.return_value = {}
            client = PIAGClient(api_token='token')

            assert client.api_token == 'token'


@pytest.mark.unit
class TestPIAGClientCollections:
    """Tests des opérations sur les collections."""

    @patch('app.piag.core.client.requests.request')
    def test_list_collections_success(self, mock_request, piag_client):
        """Test listage de collections."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {'id': 'col-1', 'name': 'Test Collection'}
            ],
            'total': 1
        }
        mock_request.return_value = mock_response

        result = piag_client.list_collections(project_id='test-project')

        assert result['total'] == 1
        assert len(result['items']) == 1
        mock_request.assert_called_once()

    @patch('app.piag.core.client.requests.request')
    def test_create_collection_success(self, mock_request, piag_client):
        """Test création de collection."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': 'new-col-123',
            'name': 'New Collection',
            'description': 'Test'
        }
        mock_request.return_value = mock_response

        result = piag_client.create_collection(
            project_id='test-project',
            name='New Collection',
            description='Test'
        )

        assert result['id'] == 'new-col-123'
        assert result['name'] == 'New Collection'

    @patch('app.piag.core.client.requests.request')
    def test_get_collection_by_id(self, mock_request, piag_client):
        """Test récupération de collection par ID."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'col-123',
            'name': 'Test Collection'
        }
        mock_request.return_value = mock_response

        result = piag_client.get_collection(collection_id='col-123')

        assert result['id'] == 'col-123'

    @patch('app.piag.core.client.requests.request')
    def test_update_collection(self, mock_request, piag_client):
        """Test mise à jour de collection."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'col-123',
            'name': 'Updated Name',
            'description': 'Updated Description'
        }
        mock_request.return_value = mock_response

        result = piag_client.update_collection(
            collection_id='col-123',
            name='Updated Name',
            description='Updated Description'
        )

        assert result['name'] == 'Updated Name'

    @patch('app.piag.core.client.requests.request')
    def test_delete_collection(self, mock_request, piag_client):
        """Test suppression de collection."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.json.return_value = {'message': 'Deleted'}
        mock_request.return_value = mock_response

        result = piag_client.delete_collection(collection_id='col-123')

        assert result == {'message': 'Deleted'}


@pytest.mark.unit
class TestPIAGClientDocuments:
    """Tests des opérations sur les documents."""

    @patch('app.piag.core.client.requests.post')
    @patch('app.piag.core.client.Path.exists')
    @patch('builtins.open', create=True)
    def test_upload_document_success(self, mock_open, mock_exists, mock_post, piag_client):
        """Test upload de document."""
        # Mock file exists
        mock_exists.return_value = True

        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': 'doc-123',
            'filename': 'test.pdf',
            'status': 'uploaded'
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Mock file - retourne des bytes
        mock_file = MagicMock()
        mock_file.read.return_value = b'fake pdf content'
        mock_open.return_value.__enter__.return_value = mock_file

        result = piag_client.upload_document(
            collection_id='col-123',
            file_path='/tmp/test.pdf'
        )

        assert result['id'] == 'doc-123'
        assert result['status'] == 'uploaded'

    @patch('app.piag.core.client.requests.request')
    def test_list_documents(self, mock_request, piag_client):
        """Test listage de documents."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {'id': 'doc-1', 'filename': 'file1.pdf'},
                {'id': 'doc-2', 'filename': 'file2.pdf'}
            ],
            'total': 2
        }
        mock_request.return_value = mock_response

        result = piag_client.list_documents(collection_id='col-123')

        assert result['total'] == 2
        assert len(result['items']) == 2

    @patch('app.piag.core.client.requests.request')
    def test_get_document(self, mock_request, piag_client):
        """Test récupération de document."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'doc-123',
            'filename': 'test.pdf',
            'chunks_count': 10
        }
        mock_request.return_value = mock_response

        result = piag_client.get_document(
            collection_id='col-123',
            document_id='doc-123'
        )

        assert result['id'] == 'doc-123'
        assert result['chunks_count'] == 10

    @patch('app.piag.core.client.requests.request')
    def test_delete_document(self, mock_request, piag_client):
        """Test suppression de document."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.json.return_value = {'message': 'Deleted'}
        mock_request.return_value = mock_response

        result = piag_client.delete_document(
            collection_id='col-123',
            document_id='doc-123'
        )

        assert result == {'message': 'Deleted'}

    @patch('app.piag.core.client.requests.request')
    def test_get_document_chunks(self, mock_request, piag_client):
        """Test récupération de chunks de document."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'chunks': [
                {'chunk_id': 1, 'text': 'Chunk 1'},
                {'chunk_id': 2, 'text': 'Chunk 2'}
            ]
        }
        mock_request.return_value = mock_response

        result = piag_client.get_document_chunks(
            collection_id='col-123',
            document_id='doc-123'
        )

        assert len(result['chunks']) == 2


@pytest.mark.unit
class TestPIAGClientSearch:
    """Tests de la recherche RAG."""

    @patch('app.piag.core.client.requests.request')
    def test_search_success(self, mock_request, piag_client):
        """Test recherche RAG."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'chunks': [
                {
                    'text': 'Result 1',
                    'score': 0.95,
                    'document_id': 'doc-1'
                },
                {
                    'text': 'Result 2',
                    'score': 0.87,
                    'document_id': 'doc-2'
                }
            ]
        }
        mock_request.return_value = mock_response

        result = piag_client.search(
            collection_id='col-123',
            query='test query',
            top_k=5
        )

        assert len(result['chunks']) == 2
        assert result['chunks'][0]['score'] == 0.95


@pytest.mark.unit
class TestPIAGClientErrorHandling:
    """Tests de gestion d'erreur."""

    @patch('app.piag.core.client.requests.request')
    def test_http_error_handling(self, mock_request, piag_client):
        """Test gestion erreur HTTP."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_request.return_value = mock_response

        with pytest.raises(Exception, match="404"):
            piag_client.list_collections(project_id='test-project')

    @patch('app.piag.core.client.requests.request')
    def test_network_error_handling(self, mock_request, piag_client):
        """Test gestion erreur réseau."""
        mock_request.side_effect = Exception("Connection timeout")

        with pytest.raises(Exception, match="timeout"):
            piag_client.search(collection_id='col-123', query='test')

    @patch('app.piag.core.client.requests.request')
    def test_invalid_json_response(self, mock_request, piag_client):
        """Test réponse JSON invalide."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_request.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid JSON"):
            piag_client.list_collections(project_id='test-project')
