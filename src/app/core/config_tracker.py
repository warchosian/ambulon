"""
Configuration Source Tracker

Ce module fournit des classes pour tracker la provenance de chaque paramètre
de configuration utilisé par les commandes ambulon.

Usage:
    from app.core.config_tracker import ConfigTracker, ConfigSource

    tracker = ConfigTracker()
    config = load_config(config_path, defaults, tracker)

    # Appliquer arguments CLI
    if args.url:
        config['url'] = args.url
        tracker.set('url', args.url, ConfigSource.CLI)

    # Afficher le rapport
    if args.show_config_sources:
        print(tracker.get_report())
        return 0
"""

from enum import Enum
from typing import Any, Dict
from dataclasses import dataclass


class ConfigSource(Enum):
    """Sources de configuration possibles."""
    CLI = "CLI Argument"
    YAML = "YAML File"
    ENV = "Environment"
    DEFAULT = "Default"


@dataclass
class ConfigValue:
    """Valeur de configuration avec sa source."""
    key: str
    value: Any
    source: ConfigSource
    is_sensitive: bool = False


class ConfigTracker:
    """Trace la provenance de chaque paramètre de configuration."""

    def __init__(self):
        """Initialise le tracker."""
        self.values: Dict[str, ConfigValue] = {}

    def set(self, key: str, value: Any, source: ConfigSource, is_sensitive: bool = False):
        """
        Enregistre une valeur avec sa source.

        Args:
            key: Nom du paramètre (ex: 'gitlab.token')
            value: Valeur du paramètre
            source: Source de la valeur (CLI, YAML, ENV, DEFAULT)
            is_sensitive: True si la valeur doit être masquée (token, password, etc.)
        """
        self.values[key] = ConfigValue(
            key=key,
            value=value,
            source=source,
            is_sensitive=is_sensitive
        )

    def get_report(self, command_name: str = "") -> str:
        """
        Génère le rapport de traçabilité complet.

        Args:
            command_name: Nom de la commande (optionnel, pour le titre)

        Returns:
            Rapport formaté en tableau
        """
        title = f"Configuration Sources Report"
        if command_name:
            title += f" - {command_name}"

        lines = [
            "",
            title,
            "=" * 70,
            "",
            f"{'Parameter':<25} {'Source':<20} {'Value':<25}",
            f"{'-' * 25} {'-' * 20} {'-' * 25}",
        ]

        # Trier par source puis par clé
        sorted_values = sorted(
            self.values.values(),
            key=lambda v: (v.source.value, v.key)
        )

        for config_value in sorted_values:
            display_value = "****** (masked)" if config_value.is_sensitive else str(config_value.value)
            # Tronquer les longues valeurs
            if len(display_value) > 25 and not config_value.is_sensitive:
                display_value = display_value[:22] + "..."
            lines.append(
                f"{config_value.key:<25} {config_value.source.value:<20} {display_value:<25}"
            )

        # Résumé par source
        summary = self._get_summary()
        lines.extend([
            "",
            "Summary:",
        ])
        for source, count in sorted(summary.items()):
            lines.append(f"  - {source:<18} {count} parameter(s)")

        return "\n".join(lines)

    def get_check_summary(self, command_name: str = "") -> str:
        """
        Génère un résumé condensé pour vérification rapide.

        Args:
            command_name: Nom de la commande (optionnel)

        Returns:
            Résumé condensé avec juste la distribution des sources
        """
        title = f"Configuration Check"
        if command_name:
            title += f" - {command_name}"

        summary = self._get_summary()

        lines = [
            "",
            title,
            "=" * 50,
            "",
            "Sources distribution:",
        ]

        # Tableau récapitulatif
        total = sum(summary.values())
        for source_name in sorted(summary.keys()):
            count = summary[source_name]
            percentage = (count / total * 100) if total > 0 else 0
            lines.append(f"  {source_name:<18} {count:>2} parameter(s)  ({percentage:>5.1f}%)")

        lines.extend([
            "",
            f"Total parameters: {total}",
            "",
            "✓ Configuration hierarchy: CLI > YAML > Environment > Default",
        ])

        # Warnings
        warnings = self._get_warnings()
        if warnings:
            lines.extend([
                "",
                "⚠️ Warnings:",
            ])
            for warning in warnings:
                lines.append(f"  - {warning}")

        return "\n".join(lines)

    def _get_summary(self) -> Dict[str, int]:
        """Compte le nombre de paramètres par source."""
        summary = {}
        for config_value in self.values.values():
            source_name = config_value.source.value
            summary[source_name] = summary.get(source_name, 0) + 1
        return summary

    def _get_warnings(self) -> list:
        """Génère des warnings basés sur la configuration."""
        warnings = []

        # Vérifier les valeurs vides dans les paramètres critiques
        for config_value in self.values.values():
            if config_value.is_sensitive and config_value.source == ConfigSource.DEFAULT:
                if not config_value.value or config_value.value == "(empty)":
                    warnings.append(f"{config_value.key} is empty (from defaults)")

        # Vérifier si des secrets viennent du YAML au lieu de ENV
        for config_value in self.values.values():
            if config_value.is_sensitive and config_value.source == ConfigSource.YAML:
                warnings.append(
                    f"{config_value.key} comes from YAML (should use environment variable)"
                )

        return warnings

    def has_value(self, key: str) -> bool:
        """Vérifie si une clé a été trackée."""
        return key in self.values

    def get_source(self, key: str) -> ConfigSource:
        """Retourne la source d'une clé."""
        if key in self.values:
            return self.values[key].source
        raise KeyError(f"Key '{key}' not found in tracker")


def is_sensitive_key(key: str) -> bool:
    """
    Détermine si une clé contient des données sensibles.

    Args:
        key: Nom de la clé à vérifier

    Returns:
        True si la clé est sensible (token, password, etc.)
    """
    sensitive_keywords = [
        'token', 'password', 'secret', 'key', 'credential',
        'apikey', 'api_key', 'pat', 'private'
    ]
    return any(keyword in key.lower() for keyword in sensitive_keywords)
