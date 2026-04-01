"""
Tests unitaires pour le module config_manager.

Tests du gestionnaire générique de configuration avec tracking automatique.
"""

import os
import pytest
import tempfile
from pathlib import Path
from app.core.config_manager import ConfigManager
from app.core.config_tracker import ConfigSource


@pytest.fixture
def temp_config_file():
    """Crée un fichier de configuration temporaire pour les tests."""
    content = """
api:
  url: https://yaml.example.com
  timeout: 60
  token: yaml_token_123

output:
  directory: ./yaml_output
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if Path(temp_path).exists():
        Path(temp_path).unlink()


@pytest.fixture
def default_config():
    """Configuration par défaut pour les tests."""
    return {
        'api': {
            'url': 'https://default.example.com',
            'timeout': 30,
            'token': ''
        },
        'output': {
            'directory': './output',
            'format': 'json'
        }
    }


@pytest.fixture
def clean_env():
    """Nettoie les variables d'environnement avant et après les tests."""
    # Sauvegarder les variables existantes
    saved_vars = {}
    env_vars_to_clean = ['MY_MODULE_URL', 'MY_MODULE_TIMEOUT', 'MY_MODULE_TOKEN']

    for var in env_vars_to_clean:
        if var in os.environ:
            saved_vars[var] = os.environ[var]
            del os.environ[var]

    yield

    # Restaurer les variables
    for var in env_vars_to_clean:
        if var in os.environ:
            del os.environ[var]

    for var, value in saved_vars.items():
        os.environ[var] = value


class TestConfigManagerInitialization:
    """Tests d'initialisation du ConfigManager."""

    def test_basic_initialization(self, default_config):
        """Teste l'initialisation basique."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        assert manager.module_name == 'test-module'
        assert manager.defaults == default_config
        assert manager.env_prefix is None
        assert manager.sensitive_keys == []
        assert manager.config == {}
        assert manager.config_file_path is None

    def test_initialization_with_env_prefix(self, default_config):
        """Teste l'initialisation avec préfixe ENV."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config,
            env_prefix='MY_MODULE'
        )

        assert manager.env_prefix == 'MY_MODULE'

    def test_initialization_with_sensitive_keys(self, default_config):
        """Teste l'initialisation avec clés sensibles."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config,
            sensitive_keys=['api_key', 'secret']
        )

        assert 'api_key' in manager.sensitive_keys
        assert 'secret' in manager.sensitive_keys


class TestConfigManagerLoad:
    """Tests de chargement de configuration."""

    def test_load_defaults_only(self, default_config, clean_env):
        """Teste le chargement avec defaults uniquement."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        config = manager.load()

        assert config['api']['url'] == 'https://default.example.com'
        assert config['api']['timeout'] == 30
        assert config['output']['directory'] == './output'

    def test_load_with_yaml(self, default_config, temp_config_file, clean_env):
        """Teste le chargement avec fichier YAML."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        config = manager.load(config_path=temp_config_file)

        # Values from YAML should override defaults
        assert config['api']['url'] == 'https://yaml.example.com'
        assert config['api']['timeout'] == 60
        assert config['api']['token'] == 'yaml_token_123'
        assert config['output']['directory'] == './yaml_output'

        # Verify config file path was set
        assert manager.config_file_path == Path(temp_config_file)

    def test_load_with_cli_overrides(self, default_config, clean_env):
        """Teste le chargement avec overrides CLI."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        cli_overrides = {
            'api.url': 'https://cli.example.com',
            'api.timeout': 120,
            'output.directory': './cli_output'
        }

        config = manager.load(cli_overrides=cli_overrides)

        assert config['api']['url'] == 'https://cli.example.com'
        assert config['api']['timeout'] == 120
        assert config['output']['directory'] == './cli_output'

    def test_load_cli_overrides_none_values(self, default_config, clean_env):
        """Teste que les overrides None ne sont pas appliqués."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        cli_overrides = {
            'api.url': None,  # Should not override
            'api.timeout': 120,  # Should override
        }

        config = manager.load(cli_overrides=cli_overrides)

        # None should not override
        assert config['api']['url'] == 'https://default.example.com'
        # Value should override
        assert config['api']['timeout'] == 120


class TestConfigManagerValidation:
    """Tests de validation de configuration."""

    def test_validate_success(self, default_config, clean_env):
        """Teste la validation avec toutes les clés requises présentes."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        cli_overrides = {
            'api.url': 'https://example.com',
            'api.token': 'token123'
        }

        manager.load(cli_overrides=cli_overrides)

        is_valid, missing = manager.validate(['api.url', 'api.token'])

        assert is_valid is True
        assert missing == []

    def test_validate_missing_keys(self, default_config, clean_env):
        """Teste la validation avec clés manquantes."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        manager.load()  # Load defaults only (token is empty)

        is_valid, missing = manager.validate(['api.url', 'api.token'])

        assert is_valid is False
        assert 'api.token' in missing

    def test_validate_empty_list(self, default_config, clean_env):
        """Teste la validation avec liste vide (toujours valide)."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        manager.load()

        is_valid, missing = manager.validate([])

        assert is_valid is True
        assert missing == []


class TestConfigManagerGetValue:
    """Tests de récupération de valeurs."""

    def test_get_value_existing(self, default_config, clean_env):
        """Teste la récupération d'une valeur existante."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        manager.load()

        assert manager.get_value('api.url') == 'https://default.example.com'
        assert manager.get_value('api.timeout') == 30

    def test_get_value_nonexistent_with_default(self, default_config, clean_env):
        """Teste la récupération d'une valeur inexistante avec default."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        manager.load()

        assert manager.get_value('nonexistent.key', 'fallback') == 'fallback'

    def test_get_value_nonexistent_without_default(self, default_config, clean_env):
        """Teste la récupération d'une valeur inexistante sans default."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        manager.load()

        assert manager.get_value('nonexistent.key') is None


class TestConfigManagerReports:
    """Tests de génération de rapports."""

    def test_get_report(self, default_config, clean_env):
        """Teste la génération du rapport détaillé."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        manager.load()

        report = manager.get_report()

        assert "test-module" in report
        assert "Configuration sources displayed successfully" in report

    def test_get_check_summary(self, default_config, clean_env):
        """Teste la génération du résumé."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        manager.load()

        summary = manager.get_check_summary()

        assert "test-module" in summary
        assert "Configuration hierarchy" in summary


class TestConfigManagerTracking:
    """Tests de tracking des sources."""

    def test_tracking_defaults(self, default_config, clean_env):
        """Teste le tracking des valeurs par défaut."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        manager.load()

        # Vérifier que les defaults sont trackés
        assert manager.tracker.has_value('api.url')
        assert manager.tracker.get_source('api.url') == ConfigSource.DEFAULT

    def test_tracking_cli_overrides(self, default_config, clean_env):
        """Teste le tracking des overrides CLI."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        cli_overrides = {
            'api.url': 'https://cli.example.com'
        }

        manager.load(cli_overrides=cli_overrides)

        # Vérifier que le CLI override est tracké
        assert manager.tracker.get_source('api.url') == ConfigSource.CLI

    def test_tracking_sensitive_values(self, default_config, clean_env):
        """Teste le tracking des valeurs sensibles."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config,
            sensitive_keys=['custom_secret']
        )

        cli_overrides = {
            'api.token': 'secret123',  # Détecté automatiquement
            'api.custom_secret': 'another_secret'  # Dans sensitive_keys
        }

        manager.load(cli_overrides=cli_overrides)

        # Vérifier que les valeurs sensibles sont masquées dans le rapport
        report = manager.get_report()
        assert 'secret123' not in report
        assert 'another_secret' not in report
        assert '****** (masked)' in report


class TestConfigManagerHierarchy:
    """Tests de respect de la hiérarchie de configuration."""

    def test_hierarchy_cli_over_yaml(self, default_config, temp_config_file, clean_env):
        """Teste que CLI écrase YAML."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        cli_overrides = {
            'api.url': 'https://cli.example.com'
        }

        config = manager.load(
            config_path=temp_config_file,
            cli_overrides=cli_overrides
        )

        # CLI should win over YAML
        assert config['api']['url'] == 'https://cli.example.com'
        assert manager.tracker.get_source('api.url') == ConfigSource.CLI

    def test_hierarchy_yaml_over_default(self, default_config, temp_config_file, clean_env):
        """Teste que YAML écrase Default."""
        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config
        )

        config = manager.load(config_path=temp_config_file)

        # YAML should win over default
        assert config['api']['url'] == 'https://yaml.example.com'
        assert config['api']['timeout'] == 60

    def test_full_hierarchy(self, default_config, temp_config_file, clean_env):
        """Teste la hiérarchie complète CLI > YAML > ENV > Default."""
        os.environ['MY_MODULE_URL'] = 'https://env.example.com'

        manager = ConfigManager(
            module_name='test-module',
            defaults=default_config,
            env_prefix='MY_MODULE'
        )

        cli_overrides = {
            'api.timeout': 999  # CLI override
        }

        config = manager.load(
            config_path=temp_config_file,
            cli_overrides=cli_overrides
        )

        # CLI wins for timeout
        assert config['api']['timeout'] == 999

        # YAML wins for url (no CLI override, no ENV var)
        assert config['api']['url'] == 'https://yaml.example.com'

        # Default wins for format (not in YAML, no CLI, no ENV)
        assert config['output']['format'] == 'json'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
