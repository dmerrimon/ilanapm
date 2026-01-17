"""
Configuration Management

Loads and manages YAML configuration files for the rules engine.
Supports hot-reloading without server restart.

Version 3.0: Enhanced to load international regulatory workflows and authorities
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Configuration loader for YAML files

    Loads all configuration files from the backend/config directory
    (Task Ontology v3.0 with international regulatory workflows)
    and provides a unified interface for accessing configuration data.
    """

    def __init__(self, config_dir: str = None):
        """
        Initialize configuration loader

        Args:
            config_dir: Directory containing YAML configuration files.
                       If None, uses backend/config for v3.0 files,
                       falls back to config-templates if not found.
        """
        if config_dir is None:
            # Try v3.0 config directory first
            v3_config_dir = Path(__file__).parent / "config"
            if v3_config_dir.exists():
                self.config_dir = v3_config_dir
                logger.info(f"Using Task Ontology v3.0 config directory: {v3_config_dir}")
            else:
                # Fallback to config-templates
                self.config_dir = Path("config-templates")
                logger.warning(f"v3.0 config directory not found, using fallback: {self.config_dir}")
        else:
            self.config_dir = Path(config_dir)

        self.config_cache = {}
        self._load_all_configs()

    def _load_all_configs(self):
        """Load all YAML configuration files"""
        # Task Ontology v3.0 configuration files
        config_files = {
            'task_ontology': 'task_ontology.yaml',  # v3.0 with international variations
            'regulatory_workflows': 'regulatory_workflows.yaml',  # NEW in v3.0
            'authorities': 'authorities.yaml',  # NEW in v3.0
            # Legacy config files (for backward compatibility)
            'authority_timelines': 'authority_timelines.yaml',
            'checklists': 'checklists.yaml',
            'duration_bounds': 'duration_bounds.yaml',
            'operational_sequences': 'operational_sequences.yaml',
            'parallelization_rules': 'parallelization_rules.yaml'
        }

        for key, filename in config_files.items():
            file_path = self.config_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.config_cache[key] = yaml.safe_load(f)
                        logger.info(f"✅ Loaded config: {filename}")
                except Exception as e:
                    logger.error(f"❌ Failed to load {filename}: {e}")
                    self.config_cache[key] = {}
            else:
                logger.warning(f"⚠️  Config file not found: {filename}")
                self.config_cache[key] = {}

    def get_config(self) -> Dict[str, Any]:
        """
        Get merged configuration dictionary

        Returns:
            Dictionary with all configuration data merged into a single structure.
            v3.0: Includes regulatory_workflows and authorities from Task Ontology v3.0
        """
        # Load v3.0 configuration data
        task_ontology_data = self.config_cache.get('task_ontology', {})
        regulatory_workflows_data = self.config_cache.get('regulatory_workflows', {})
        authorities_data = self.config_cache.get('authorities', {})

        config = {
            # v3.0 configuration
            'task_ontology': task_ontology_data.get('tasks', []),
            'regulatory_workflows': regulatory_workflows_data.get('regulatory_workflows', []),
            'authorities': authorities_data.get('authorities', []),

            # Legacy configuration (for backward compatibility)
            'authority_timelines': self.config_cache.get('authority_timelines', {}).get('authorities', {}),
            'checklists': self.config_cache.get('checklists', {}).get('checklists', {}),
            'duration_bounds': self.config_cache.get('duration_bounds', {}).get('duration_rules', []),
            'operational_sequences': self.config_cache.get('operational_sequences', {}).get('sequences', []),
            'parallelization_rules': self.config_cache.get('parallelization_rules', {}).get('rules', []),

            # Metadata
            'ontology_version': task_ontology_data.get('version', 'unknown'),
            'config_dir': str(self.config_dir)
        }

        return config

    def reload(self):
        """Reload all configuration files (for hot-reload)"""
        logger.info("♻️  Reloading configuration...")
        self._load_all_configs()
        logger.info("✅ Configuration reloaded successfully")


# Global config loader instance
_config_loader = None


def load_config() -> Dict[str, Any]:
    """
    Get current configuration

    Returns:
        Dictionary with all configuration data
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader.get_config()


def reload_config():
    """
    Reload configuration from disk

    Useful for hot-reloading configuration changes without restarting server.
    """
    global _config_loader
    if _config_loader:
        _config_loader.reload()
    else:
        _config_loader = ConfigLoader()


def get_config_loader() -> ConfigLoader:
    """
    Get the config loader instance

    Returns:
        ConfigLoader instance
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


__all__ = ['load_config', 'reload_config', 'get_config_loader', 'ConfigLoader']
