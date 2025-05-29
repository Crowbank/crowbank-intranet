"""
YAML Configuration Loader for Crowbank Intranet.

This module provides functions to load application configuration from YAML files:
1. Default config values (config/yaml/default.yaml)
2. Environment-specific overrides (config/yaml/dev.yaml, etc.)
3. Secret config values (config/yaml/secret.yaml)
"""

import os
import sys
from typing import Dict, Any, Optional, List
import yaml
from collections import defaultdict
import logging


# Create a logger for the config loader
logger = logging.getLogger(__name__)


def deep_merge(source: Dict, destination: Dict) -> Dict:
    """
    Deep merge two dictionaries.
    
    Args:
        source: Source dictionary
        destination: Destination dictionary (will be modified)
        
    Returns:
        Merged dictionary
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # Get node or create empty dict
            node = destination.setdefault(key, {})
            if isinstance(node, dict):
                deep_merge(value, node)
            else:
                # If destination key exists but is not a dict, override it
                destination[key] = value
        elif isinstance(value, list):
            # If it's a list, merge if destination has a list, otherwise override
            if key in destination and isinstance(destination[key], list):
                destination[key].extend(value)
            else:
                destination[key] = value
        else:
            # For simple values, just override
            destination[key] = value
    return destination


def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    Load YAML from file.
    
    Args:
        file_path: Path to YAML file
        
    Returns:
        Dictionary with config data, empty dict if file not found
    """
    try:
        with open(file_path, 'r') as file:
            config_data = yaml.safe_load(file) or {}
            return config_data
    except FileNotFoundError:
        logger.warning(f"Config file not found: {file_path}")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML in {file_path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading config file {file_path}: {e}")
        return {}


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Flatten a nested dictionary with keys joined by separator.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key for nested dictionaries
        sep: Separator for keys
        
    Returns:
        Flattened dictionary
    """
    flat_dict = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            flat_dict.update(flatten_dict(v, new_key, sep))
        else:
            flat_dict[new_key.upper()] = v
    return flat_dict


def load_config(env: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML files.
    
    Args:
        env: Optional environment name to override FLASK_ENV.
             Should be one of: 'dev', 'test', 'prod'
    
    Returns:
        A dictionary containing all configuration settings.
    """
    # Base config directory
    config_dir = os.path.join(os.getcwd(), 'config', 'yaml')
    
    # 1. Determine environment
    flask_env = env or os.getenv("FLASK_ENV", "dev")
    
    # Convert to short name format if full name was used
    if flask_env == "development":
        flask_env = "dev"
    elif flask_env == "production":
        flask_env = "prod"
    elif flask_env == "testing":
        flask_env = "test"
    
    # 2. Load default config
    default_config_path = os.path.join(config_dir, 'default.yaml')
    config = load_yaml_file(default_config_path)
    
    # 3. Load environment-specific config
    env_config_path = os.path.join(config_dir, f"{flask_env}.yaml")
    env_config = load_yaml_file(env_config_path)
    
    # Deep merge environment config on top of default config
    config = deep_merge(env_config, config)
    
    # 4. Load secret config (if exists)
    secret_config_path = os.path.join(config_dir, 'secret.yaml')
    secret_config = load_yaml_file(secret_config_path)
    
    # Deep merge secret config on top of existing config
    config = deep_merge(secret_config, config)
    
    # 5. Add environment info
    config['env'] = flask_env
    
    # 6. Create database URL if all parts are present
    if 'database' in config:
        db = config.get('database', {})
        if all(k in db for k in ['user', 'password', 'host', 'name']):
            port = db.get('port', '')
            port_str = f":{port}" if port else ""
            config.setdefault('sqlalchemy', {})
            config['sqlalchemy']['database_uri'] = (
                f"postgresql://{db['user']}:{db['password']}@{db['host']}{port_str}/{db['name']}"
            )
    
    # 7. Create a Flask-style flattened config for compatibility
    flask_config = flatten_dict(config)
    
    return {
        'nested': config,  # The original nested structure
        'flat': flask_config  # Flattened for Flask compatibility
    }


def get_config_value(path: str, default: Any = None) -> Any:
    """
    Get a specific configuration value using dot notation.
    
    Args:
        path: The configuration key path (e.g., 'database.host')
        default: Default value if key is not found
    
    Returns:
        The configuration value or the default value if not found
    """
    config = load_config()['nested']
    keys = path.split('.')
    
    # Traverse the nested dictionary
    for key in keys:
        if isinstance(config, dict) and key in config:
            config = config[key]
        else:
            return default
    
    return config
