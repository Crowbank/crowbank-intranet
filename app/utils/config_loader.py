"""
Configuration loader for the Crowbank Intranet.

This module provides functions to load application configuration
from multiple sources in a defined order:
1. Default config values
2. Environment-specific overrides
3. Secrets from environment variables or .env file
4. Command-line arguments (if applicable)
"""

import os
import sys
from typing import Dict, Any, Optional
from dotenv import load_dotenv


def load_config(env: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from multiple sources.
    
    Args:
        env: Optional environment name to override FLASK_ENV.
             Should be one of: 'dev', 'test', 'prod'
    
    Returns:
        A dictionary containing all configuration settings.
    """
    config = {}
    
    # 1. Load base settings
    try:
        from config.default import config as default_config
        config.update(default_config)
    except ImportError:
        print("Warning: Could not import default configuration", file=sys.stderr)
    
    # 2. Determine environment
    flask_env = env or os.getenv("FLASK_ENV", "dev")
    
    # Convert to short name format if full name was used
    if flask_env == "development":
        flask_env = "dev"
    elif flask_env == "production":
        flask_env = "prod"
    elif flask_env == "testing":
        flask_env = "test"
    
    # Store the environment in the config
    config["ENV"] = flask_env
    
    # 3. Load environment-specific settings
    try:
        if flask_env == "prod":
            from config.prod import config as env_config
        elif flask_env == "test":
            from config.test import config as env_config
        else:  # dev is default
            from config.dev import config as env_config
        
        config.update(env_config)
    except ImportError:
        print(f"Warning: Could not import {flask_env} configuration", file=sys.stderr)
    
    # 4. Load secrets from environment variables or .env file
    # For production, this could be skipped if using system environment variables
    if flask_env != "prod":
        # Try to load from .env file first
        dotenv_path = os.getenv("DOTENV_PATH", ".env")
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
        # If .env doesn't exist, try dev.config
        elif os.path.exists("dev.config"):
            # We don't need to load it here since run_dev.sh should export the variables,
            # but this is a fallback in case someone runs the application directly
            load_dotenv("dev.config")
    
    # 5. Override with environment variables that match config keys
    for key in list(config.keys()):
        env_key = key.upper()  # Environment variables are typically uppercase
        env_val = os.getenv(env_key)
        if env_val is not None:
            # Convert environment string values to appropriate types
            if isinstance(config[key], bool):
                config[key] = env_val.lower() in ('true', 'yes', '1', 't', 'y')
            elif isinstance(config[key], int):
                config[key] = int(env_val)
            elif isinstance(config[key], float):
                config[key] = float(env_val)
            elif isinstance(config[key], (list, tuple)) and env_val:
                config[key] = [item.strip() for item in env_val.split(',')]
            elif isinstance(config[key], dict):
                # Skip complex types like dictionaries
                pass
            else:
                config[key] = env_val
    
    # 6. Special handling for database configuration
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        config["SQLALCHEMY_DATABASE_URI"] = db_url
    
    # 7. Handle credentials individually
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    
    if all([db_user, db_password, db_host, db_name]):
        port_str = f":{db_port}" if db_port else ""
        config["SQLALCHEMY_DATABASE_URI"] = (
            f"postgresql://{db_user}:{db_password}@{db_host}{port_str}/{db_name}"
        )
    
    return config


def get_config_value(key: str, default: Any = None, env: Optional[str] = None) -> Any:
    """
    Get a specific configuration value.
    
    Args:
        key: The configuration key to retrieve
        default: Default value if key is not found
        env: Optional environment name to override FLASK_ENV
    
    Returns:
        The configuration value or the default value if not found
    """
    config = load_config(env)
    return config.get(key, default) 