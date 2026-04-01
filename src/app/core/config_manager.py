"""
Generic Configuration Manager with Source Tracking

Ce module fournit un gestionnaire de configuration générique qui :
- Charge la configuration depuis multiple sources (CLI, YAML, ENV, defaults)
- Respecte la hiérarchie : CLI > YAML > ENV > Default
- Track automatiquement la provenance de chaque paramètre
- Fournit des méthodes de diagnostic (--show-config-sources, --check-config)

Usage:
    from app.core.config_manager import ConfigManager

    # Définir les defaults
    defaults = {
        'api': {
            'url': 'https://default.example.com',
            'timeout': 30
        }
    }

    # Créer le gestionnaire
    manager = ConfigManager(
        module_name='my-module',
        defaults=defaults,
        env_prefix='MY_MODULE'
    )

    # Charger la configuration
    config = manager.load(
        config_path=args.config,
        cli_overrides={
            'api.url': args.url if args.url else None,
            'api.timeout': args.timeout if args.timeout else None
        }
    )

    # Afficher le rapport si demandé
    if args.show_config_sources:
        print(manager.get_report())
        return 0
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List
from app.core.config_loader import load_config as load_app_config
from app.core.config_tracker import ConfigTracker, ConfigSource, is_sensitive_key

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Gestionnaire générique de configuration avec tracking des sources.

    Ce gestionnaire centralise toute la logique de chargement de configuration
    et de tracking des sources pour les modules ambulon.
    """

    def __init__(
        self,
        module_name: str,
        defaults: Dict[str, Any],
        env_prefix: Optional[str] = None,
        sensitive_keys: Optional[List[str]] = None
    ):
        """
        Initialise le gestionnaire de configuration.

        Args:
            module_name: Nom du module (pour affichage dans les rapports)
            defaults: Configuration par défaut (dict imbriqué)
            env_prefix: Préfixe pour les variables d'environnement (ex: 'GITLAB')
            sensitive_keys: Liste de clés sensibles supplémentaires (optionnel)
        """
        self.module_name = module_name
        self.defaults = defaults
        self.env_prefix = env_prefix
        self.sensitive_keys = sensitive_keys or []
        self.tracker = ConfigTracker()
        self.config: Dict[str, Any] = {}
        self.config_file_path: Optional[Path] = None

    def load(
        self,
        config_path: Optional[str] = None,
        cli_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Charge la configuration depuis toutes les sources avec tracking.

        Args:
            config_path: Chemin vers le fichier YAML de configuration (optionnel)
            cli_overrides: Dict des overrides CLI (key: value ou None si pas fourni)

        Returns:
            Configuration finale fusionnée
        """
        # 1. Track defaults
        self._track_defaults()

        # 2. Load from YAML + ENV substitution
        if config_path:
            self.config = load_app_config(config_path, self.defaults)
            config_file_resolved = Path(config_path).expanduser()
            if config_file_resolved.exists():
                self.config_file_path = config_file_resolved
                self._track_loaded_config()
        else:
            self.config = self.defaults.copy()

        # 3. Track direct environment variables
        self._track_env_vars()

        # 4. Apply CLI overrides (highest priority)
        if cli_overrides:
            self._apply_cli_overrides(cli_overrides)

        return self.config

    def _track_defaults(self):
        """Track les valeurs par défaut."""
        for section, section_values in self.defaults.items():
            if isinstance(section_values, dict):
                for key, value in section_values.items():
                    full_key = f"{section}.{key}"
                    display_value = self._format_value(value)
                    is_sensitive = self._is_sensitive(key)
                    self.tracker.set(full_key, display_value, ConfigSource.DEFAULT, is_sensitive)

    def _track_loaded_config(self):
        """Track les valeurs chargées depuis YAML (avec substitution ENV)."""
        for section, section_values in self.config.items():
            if isinstance(section_values, dict):
                for key, value in section_values.items():
                    full_key = f"{section}.{key}"
                    default_value = self.defaults.get(section, {}).get(key)

                    # Si différent du default, vient du YAML ou ENV
                    if value != default_value:
                        # Essayer de déterminer si c'est ENV ou YAML
                        source = self._determine_source(section, key, value)
                        display_value = self._format_value(value)
                        is_sensitive = self._is_sensitive(key)
                        self.tracker.set(full_key, display_value, source, is_sensitive)

    def _track_env_vars(self):
        """Track les variables d'environnement directes (non via YAML)."""
        if not self.env_prefix:
            return

        # Mapping des variables d'env vers les clés de config
        # Format: ENV_VAR -> (section, key)
        env_mappings = self._build_env_mappings()

        for env_var, (section, key) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                full_key = f"{section}.{key}"
                # Vérifier si déjà tracké par YAML
                if not self.tracker.has_value(full_key):
                    # Appliquer à la config
                    self.config.setdefault(section, {})[key] = env_value
                    display_value = self._format_value(env_value)
                    is_sensitive = self._is_sensitive(key)
                    self.tracker.set(full_key, display_value, ConfigSource.ENV, is_sensitive)
                else:
                    # Si déjà tracké, vérifier si c'est bien ENV
                    existing_source = self.tracker.get_source(full_key)
                    if existing_source == ConfigSource.DEFAULT:
                        # Écraser le default par ENV
                        self.config.setdefault(section, {})[key] = env_value
                        display_value = self._format_value(env_value)
                        is_sensitive = self._is_sensitive(key)
                        self.tracker.set(full_key, display_value, ConfigSource.ENV, is_sensitive)

    def _apply_cli_overrides(self, cli_overrides: Dict[str, Any]):
        """
        Applique les overrides CLI (priorité maximale).

        Args:
            cli_overrides: Dict {full_key: value ou None}
                          Ex: {'api.url': 'https://...', 'api.timeout': None}
        """
        for full_key, value in cli_overrides.items():
            if value is not None:  # Only apply if CLI arg was provided
                # Parse le full_key (ex: 'api.url' -> section='api', key='url')
                parts = full_key.split('.')
                if len(parts) == 2:
                    section, key = parts
                    self.config.setdefault(section, {})[key] = value
                    display_value = self._format_value(value)
                    is_sensitive = self._is_sensitive(key)
                    self.tracker.set(full_key, display_value, ConfigSource.CLI, is_sensitive)

    def _build_env_mappings(self) -> Dict[str, tuple]:
        """
        Construit le mapping des variables d'environnement.

        Returns:
            Dict {ENV_VAR_NAME: (section, key)}
        """
        mappings = {}
        if not self.env_prefix:
            return mappings

        # Auto-générer les mappings depuis defaults
        for section, section_values in self.defaults.items():
            if isinstance(section_values, dict):
                for key in section_values.keys():
                    # Format: {ENV_PREFIX}_{KEY}
                    env_var = f"{self.env_prefix}_{key.upper()}"
                    mappings[env_var] = (section, key)

        return mappings

    def _determine_source(self, section: str, key: str, value: Any) -> ConfigSource:
        """
        Détermine si une valeur vient de YAML ou ENV (via substitution).

        Args:
            section: Section de config
            key: Clé de config
            value: Valeur actuelle

        Returns:
            ConfigSource.YAML ou ConfigSource.ENV
        """
        # Vérifier si la valeur correspond à une var d'env
        if self.env_prefix:
            env_var = f"{self.env_prefix}_{key.upper()}"
            env_value = os.getenv(env_var)
            if env_value and str(value) == str(env_value):
                return ConfigSource.ENV

        # Par défaut, considérer comme YAML
        return ConfigSource.YAML

    def _is_sensitive(self, key: str) -> bool:
        """Détermine si une clé est sensible."""
        if key in self.sensitive_keys:
            return True
        return is_sensitive_key(key)

    def _format_value(self, value: Any) -> str:
        """Formate une valeur pour affichage."""
        if value is None or value == '':
            return "(empty)"
        if isinstance(value, list):
            return f"{len(value)} items" if value else "(empty)"
        if isinstance(value, dict):
            return f"{len(value)} entries" if value else "(empty)"
        return str(value)

    def get_report(self) -> str:
        """
        Génère le rapport complet de traçabilité.

        Returns:
            Rapport formaté
        """
        report = self.tracker.get_report(self.module_name)

        if self.config_file_path:
            report += f"\n\nConfig file: {self.config_file_path}"
        else:
            report += f"\n\nConfig file: (not found, using defaults)"

        report += "\n\n✓ Configuration sources displayed successfully"
        report += "\nUse this command without -S to execute normally."

        return report

    def get_check_summary(self) -> str:
        """
        Génère le résumé de vérification.

        Returns:
            Résumé condensé
        """
        summary = self.tracker.get_check_summary(self.module_name)

        if self.config_file_path:
            summary += f"\n\nConfig file: {self.config_file_path}"
        else:
            summary += f"\n\nConfig file: (not found)"

        summary += "\nUse -S/--show-config-sources for detailed view."

        return summary

    def validate(self, required_keys: List[str]) -> tuple[bool, List[str]]:
        """
        Valide que les clés requises sont présentes et non vides.

        Args:
            required_keys: Liste de full_keys requis (ex: ['api.url', 'api.token'])

        Returns:
            (is_valid, missing_keys)
        """
        missing = []

        for full_key in required_keys:
            parts = full_key.split('.')
            if len(parts) == 2:
                section, key = parts
                value = self.config.get(section, {}).get(key)
                if not value or value == '' or (isinstance(value, list) and not value):
                    missing.append(full_key)

        return (len(missing) == 0, missing)

    def get_value(self, full_key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration.

        Args:
            full_key: Clé complète (ex: 'api.url')
            default: Valeur par défaut si non trouvée

        Returns:
            Valeur de configuration
        """
        parts = full_key.split('.')
        if len(parts) == 2:
            section, key = parts
            return self.config.get(section, {}).get(key, default)
        return default
