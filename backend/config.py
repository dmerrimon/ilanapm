"""
Configuration Management

Loads and manages YAML configuration files for the rules engine.
Supports hot-reloading without server restart.
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

    Loads all configuration files from the config-templates directory
    and provides a unified interface for accessing configuration data.
    """

    def __init__(self, config_dir: str = "config-templates"):
        """
        Initialize configuration loader

        Args:
            config_dir: Directory containing YAML configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_cache = {}
        self._load_all_configs()

    def _load_all_configs(self):
        """Load all YAML configuration files"""
        config_files = {
            'authority_timelines': 'authority_timelines.yaml',
            'task_ontology': 'task_ontology.yaml',
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
            Dictionary with all configuration data merged into a single structure
        """
        return {
            'authorities': self.config_cache.get('authority_timelines', {}).get('authorities', {}),
            'task_ontology': self.config_cache.get('task_ontology', {}).get('tasks', []),
            'checklists': self.config_cache.get('checklists', {}).get('checklists', {}),
            'duration_bounds': self.config_cache.get('duration_bounds', {}).get('duration_rules', []),
            'operational_sequences': self.config_cache.get('operational_sequences', {}).get('sequences', []),
            'parallelization_rules': self.config_cache.get('parallelization_rules', {}).get('rules', [])
        }

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
