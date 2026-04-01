"""
Tests unitaires pour le module config_tracker.

Tests de tracking des sources de configuration pour respecter la hiérarchie :
CLI > YAML > Environment > Default
"""

import pytest
from src.app.core.config_tracker import (
    ConfigTracker,
    ConfigSource,
    ConfigValue,
    is_sensitive_key
)


class TestConfigSource:
    """Tests pour l'énumération ConfigSource."""

    def test_config_source_values(self):
        """Vérifie que les valeurs de l'enum sont correctes."""
        assert ConfigSource.CLI.value == "CLI Argument"
        assert ConfigSource.YAML.value == "YAML File"
        assert ConfigSource.ENV.value == "Environment"
        assert ConfigSource.DEFAULT.value == "Default"


class TestConfigValue:
    """Tests pour la dataclass ConfigValue."""

    def test_config_value_creation(self):
        """Teste la création d'une ConfigValue."""
        cv = ConfigValue(
            key="api.url",
            value="https://example.com",
            source=ConfigSource.CLI,
            is_sensitive=False
        )

        assert cv.key == "api.url"
        assert cv.value == "https://example.com"
        assert cv.source == ConfigSource.CLI
        assert cv.is_sensitive is False

    def test_config_value_sensitive(self):
        """Teste une ConfigValue sensible."""
        cv = ConfigValue(
            key="api.token",
            value="secret123",
            source=ConfigSource.ENV,
            is_sensitive=True
        )

        assert cv.is_sensitive is True
        assert cv.value == "secret123"


class TestIsSensitiveKey:
    """Tests pour la fonction is_sensitive_key."""

    def test_token_keys(self):
        """Vérifie que les clés avec 'token' sont détectées."""
        assert is_sensitive_key("api_token") is True
        assert is_sensitive_key("auth_token") is True
        assert is_sensitive_key("bearer_token") is True
        assert is_sensitive_key("TOKEN") is True

    def test_password_keys(self):
        """Vérifie que les clés avec 'password' sont détectées."""
        assert is_sensitive_key("password") is True
        assert is_sensitive_key("db_password") is True
        assert is_sensitive_key("PASSWORD") is True

    def test_secret_keys(self):
        """Vérifie que les clés avec 'secret' sont détectées."""
        assert is_sensitive_key("secret") is True
        assert is_sensitive_key("api_secret") is True
        assert is_sensitive_key("client_secret") is True

    def test_key_keys(self):
        """Vérifie que les clés avec 'key' sont détectées."""
        assert is_sensitive_key("api_key") is True
        assert is_sensitive_key("private_key") is True
        assert is_sensitive_key("apikey") is True

    def test_credential_keys(self):
        """Vérifie que les clés avec 'credential' sont détectées."""
        assert is_sensitive_key("credential") is True
        assert is_sensitive_key("credentials") is True
        assert is_sensitive_key("user_credential") is True

    def test_non_sensitive_keys(self):
        """Vérifie que les clés normales ne sont pas détectées comme sensibles."""
        assert is_sensitive_key("url") is False
        assert is_sensitive_key("timeout") is False
        assert is_sensitive_key("max_retries") is False
        assert is_sensitive_key("output_directory") is False


class TestConfigTracker:
    """Tests pour la classe ConfigTracker."""

    def test_initialization(self):
        """Teste l'initialisation du tracker."""
        tracker = ConfigTracker()
        assert isinstance(tracker.values, dict)
        assert len(tracker.values) == 0

    def test_set_value(self):
        """Teste l'enregistrement d'une valeur."""
        tracker = ConfigTracker()
        tracker.set("api.url", "https://example.com", ConfigSource.CLI)

        assert "api.url" in tracker.values
        assert tracker.values["api.url"].value == "https://example.com"
        assert tracker.values["api.url"].source == ConfigSource.CLI
        assert tracker.values["api.url"].is_sensitive is False

    def test_set_sensitive_value(self):
        """Teste l'enregistrement d'une valeur sensible."""
        tracker = ConfigTracker()
        tracker.set("api.token", "secret123", ConfigSource.ENV, is_sensitive=True)

        assert "api.token" in tracker.values
        assert tracker.values["api.token"].is_sensitive is True

    def test_set_multiple_values(self):
        """Teste l'enregistrement de plusieurs valeurs."""
        tracker = ConfigTracker()
        tracker.set("api.url", "https://example.com", ConfigSource.CLI)
        tracker.set("api.timeout", 30, ConfigSource.DEFAULT)
        tracker.set("api.token", "secret", ConfigSource.ENV, is_sensitive=True)

        assert len(tracker.values) == 3

    def test_set_override_value(self):
        """Teste l'écrasement d'une valeur existante."""
        tracker = ConfigTracker()
        tracker.set("api.url", "https://default.com", ConfigSource.DEFAULT)
        tracker.set("api.url", "https://cli.com", ConfigSource.CLI)

        # La dernière valeur écrase la première
        assert tracker.values["api.url"].value == "https://cli.com"
        assert tracker.values["api.url"].source == ConfigSource.CLI

    def test_get_summary(self):
        """Teste le résumé des sources."""
        tracker = ConfigTracker()
        tracker.set("param1", "value1", ConfigSource.CLI)
        tracker.set("param2", "value2", ConfigSource.CLI)
        tracker.set("param3", "value3", ConfigSource.YAML)
        tracker.set("param4", "value4", ConfigSource.DEFAULT)

        summary = tracker._get_summary()

        assert summary["CLI Argument"] == 2
        assert summary["YAML File"] == 1
        assert summary["Default"] == 1

    def test_get_report_basic(self):
        """Teste la génération du rapport basique."""
        tracker = ConfigTracker()
        tracker.set("api.url", "https://example.com", ConfigSource.CLI)
        tracker.set("api.timeout", 30, ConfigSource.DEFAULT)

        report = tracker.get_report("test-command")

        assert "Configuration Sources Report - test-command" in report
        assert "api.url" in report
        assert "https://example.com" in report
        assert "CLI Argument" in report
        assert "api.timeout" in report
        assert "30" in report
        assert "Default" in report
        assert "Summary:" in report

    def test_get_report_masks_sensitive(self):
        """Teste que le rapport masque les valeurs sensibles."""
        tracker = ConfigTracker()
        tracker.set("api.token", "secret123", ConfigSource.ENV, is_sensitive=True)

        report = tracker.get_report()

        assert "secret123" not in report
        assert "****** (masked)" in report

    def test_get_check_summary(self):
        """Teste le résumé condensé."""
        tracker = ConfigTracker()
        tracker.set("param1", "value1", ConfigSource.CLI)
        tracker.set("param2", "value2", ConfigSource.YAML)
        tracker.set("param3", "value3", ConfigSource.DEFAULT)

        summary = tracker.get_check_summary("test-command")

        assert "Configuration Check - test-command" in summary
        assert "Sources distribution:" in summary
        assert "Total parameters: 3" in summary
        assert "CLI Argument" in summary
        assert "YAML File" in summary
        assert "Default" in summary

    def test_get_warnings_empty_sensitive_default(self):
        """Teste les warnings pour valeurs sensibles vides."""
        tracker = ConfigTracker()
        tracker.set("api.token", "", ConfigSource.DEFAULT, is_sensitive=True)

        warnings = tracker._get_warnings()

        assert len(warnings) == 1
        assert "api.token is empty (from defaults)" in warnings[0]

    def test_get_warnings_token_from_yaml(self):
        """Teste les warnings pour tokens dans YAML."""
        tracker = ConfigTracker()
        tracker.set("api.token", "secret123", ConfigSource.YAML, is_sensitive=True)

        warnings = tracker._get_warnings()

        assert len(warnings) == 1
        assert "api.token comes from YAML" in warnings[0]
        assert "should use environment variable" in warnings[0]

    def test_has_value(self):
        """Teste la vérification de présence d'une clé."""
        tracker = ConfigTracker()
        tracker.set("api.url", "https://example.com", ConfigSource.CLI)

        assert tracker.has_value("api.url") is True
        assert tracker.has_value("api.token") is False

    def test_get_source(self):
        """Teste la récupération de la source d'une clé."""
        tracker = ConfigTracker()
        tracker.set("api.url", "https://example.com", ConfigSource.CLI)

        assert tracker.get_source("api.url") == ConfigSource.CLI

    def test_get_source_missing_key(self):
        """Teste la récupération de source pour une clé inexistante."""
        tracker = ConfigTracker()

        with pytest.raises(KeyError, match="Key 'nonexistent' not found"):
            tracker.get_source("nonexistent")

    def test_hierarchy_tracking(self):
        """Teste le tracking complet de la hiérarchie de configuration."""
        tracker = ConfigTracker()

        # Simuler la hiérarchie : Default < ENV < YAML < CLI
        tracker.set("url", "https://default.com", ConfigSource.DEFAULT)
        tracker.set("timeout", 30, ConfigSource.DEFAULT)
        tracker.set("token", "", ConfigSource.DEFAULT, is_sensitive=True)
        tracker.set("output", "./output", ConfigSource.DEFAULT)

        # ENV écrase DEFAULT
        tracker.set("url", "https://env.com", ConfigSource.ENV)

        # YAML écrase ENV et DEFAULT
        tracker.set("timeout", 60, ConfigSource.YAML)

        # CLI écrase tout
        tracker.set("output", "./custom", ConfigSource.CLI)

        # Vérifier les valeurs finales
        assert tracker.values["url"].source == ConfigSource.ENV
        assert tracker.values["url"].value == "https://env.com"

        assert tracker.values["timeout"].source == ConfigSource.YAML
        assert tracker.values["timeout"].value == 60

        assert tracker.values["output"].source == ConfigSource.CLI
        assert tracker.values["output"].value == "./custom"

        assert tracker.values["token"].source == ConfigSource.DEFAULT
        assert tracker.values["token"].value == ""

        # Vérifier le summary
        summary = tracker._get_summary()
        assert summary["CLI Argument"] == 1
        assert summary["YAML File"] == 1
        assert summary["Environment"] == 1
        assert summary["Default"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
