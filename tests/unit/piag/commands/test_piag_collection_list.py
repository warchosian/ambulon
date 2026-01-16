"""Tests unitaires mockés pour piag_collection_list."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from app.piag.commands.piag_collection_list import main


@pytest.fixture
def mock_config():
    """Fixture de configuration mockée."""
    return {
        'api': {
            'base_url': 'https://test.api.example.com',
            'timeout': 30
        },
        'project': {
            'project_id': 'test-project-id'
        },
        'security': {
            'token': 'test-token-123',
            'token_env_var': 'PIAG_RAG_API_TOKEN'
        },
        'listing': {
            'default_limit': 20,
            'default_offset': 0,
            'default_order_by': 'name',
            'default_order': 'asc'
        }
    }


@pytest.fixture
def mock_collections_response():
    """Fixture de réponse API mockée."""
    return {
        'items': [
            {'id': 'col-1', 'name': 'Collection 1', 'description': 'Test 1'},
            {'id': 'col-2', 'name': 'Collection 2', 'description': 'Test 2'}
        ],
        'total': 2,
        'limit': 20,
        'offset': 0
    }


@pytest.mark.unit
class TestPiagCollectionListCommand:
    """Tests de la commande piag-collection-list."""

    @patch('app.piag.commands.piag_collection_list.load_config')
    @patch('app.piag.commands.piag_collection_list.PIAGClient')
    def test_list_collections_with_all_args(self, mock_client_class, mock_load_config, mock_config, mock_collections_response):
        """Test avec tous les arguments CLI fournis."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.list_collections.return_value = mock_collections_response
        mock_client_class.return_value = mock_client

        args = [
            '--project-id', 'cli-project',
            '--token', 'cli-token',
            '--limit', '10',
            '--offset', '5',
            '--order-by', 'created_at',
            '--order', 'desc'
        ]

        result = main(args)

        assert result == 0
        mock_client.list_collections.assert_called_once_with(
            project_id='cli-project',
            limit=10,
            offset=5,
            order_by='created_at',
            order='desc'
        )

    @patch('app.piag.commands.piag_collection_list.load_config')
    @patch('app.piag.commands.piag_collection_list.PIAGClient')
    def test_list_collections_from_config(self, mock_client_class, mock_load_config, mock_config, mock_collections_response):
        """Test en chargeant depuis la config YAML."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.list_collections.return_value = mock_collections_response
        mock_client_class.return_value = mock_client

        args = []  # Pas d'arguments CLI

        result = main(args)

        assert result == 0
        # Vérifie que project_id vient de la config
        call_kwargs = mock_client.list_collections.call_args.kwargs
        assert call_kwargs['project_id'] == 'test-project-id'
        assert call_kwargs['limit'] == 20

    @patch('app.piag.commands.piag_collection_list.load_config')
    @patch('app.piag.commands.piag_collection_list.PIAGClient')
    @patch.dict('os.environ', {'PIAG_RAG_PROJECT_ID': 'env-project', 'PIAG_RAG_API_TOKEN': 'env-token'})
    def test_list_collections_from_env(self, mock_client_class, mock_load_config, mock_collections_response):
        """Test en chargeant depuis les variables d'environnement."""
        mock_load_config.return_value = {}  # Config vide

        mock_client = MagicMock()
        mock_client.list_collections.return_value = mock_collections_response
        mock_client_class.return_value = mock_client

        args = []

        result = main(args)

        assert result == 0
        call_kwargs = mock_client.list_collections.call_args.kwargs
        assert call_kwargs['project_id'] == 'env-project'

    @patch('app.piag.commands.piag_collection_list.load_config')
    def test_list_collections_missing_project_id(self, mock_load_config):
        """Test erreur si project_id manquant."""
        mock_load_config.return_value = {}  # Config vide, pas d'env

        args = ['--token', 'test-token']

        result = main(args)

        assert result == 1  # Erreur

    @patch('app.piag.commands.piag_collection_list.load_config')
    def test_list_collections_missing_token(self, mock_load_config, mock_config):
        """Test erreur si token manquant."""
        config_no_token = mock_config.copy()
        del config_no_token['security']['token']
        mock_load_config.return_value = config_no_token

        args = ['--project-id', 'test-project']

        result = main(args)

        assert result == 1  # Erreur

    @patch('app.piag.commands.piag_collection_list.load_config')
    @patch('app.piag.commands.piag_collection_list.PIAGClient')
    def test_list_collections_api_error(self, mock_client_class, mock_load_config, mock_config):
        """Test gestion d'erreur API."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.list_collections.side_effect = Exception("API Error: 500")
        mock_client_class.return_value = mock_client

        args = ['--project-id', 'test', '--token', 'test-token']

        result = main(args)

        assert result == 1  # Erreur

    @patch('app.piag.commands.piag_collection_list.load_config')
    @patch('app.piag.commands.piag_collection_list.PIAGClient')
    def test_list_collections_hierarchy_cli_over_yaml(self, mock_client_class, mock_load_config, mock_config, mock_collections_response):
        """Test hiérarchie: CLI écrase YAML."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.list_collections.return_value = mock_collections_response
        mock_client_class.return_value = mock_client

        args = [
            '--project-id', 'cli-project-override',
            '--limit', '50'
        ]

        result = main(args)

        assert result == 0
        call_kwargs = mock_client.list_collections.call_args.kwargs
        # CLI doit écraser la config
        assert call_kwargs['project_id'] == 'cli-project-override'
        assert call_kwargs['limit'] == 50

    @patch('app.piag.commands.piag_collection_list.load_config')
    @patch('app.piag.commands.piag_collection_list.PIAGClient')
    def test_list_collections_debug_mode(self, mock_client_class, mock_load_config, mock_config, mock_collections_response):
        """Test mode debug."""
        mock_load_config.return_value = mock_config

        mock_client = MagicMock()
        mock_client.list_collections.return_value = mock_collections_response
        mock_client_class.return_value = mock_client

        args = ['--project-id', 'test', '--token', 'test-token', '--debug']

        result = main(args)

        assert result == 0
        # Vérifie que le client reçoit une config avec debug activé
        client_config = mock_client_class.call_args.kwargs['config']
        assert client_config.get('logging', {}).get('enable_debug') is True
