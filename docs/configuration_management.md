# Configuration Management

This document outlines the configuration management strategy for the Crowbank Intranet system.

## Overview

The Crowbank Intranet application uses a centralized configuration management approach based on Flask's native configuration system, with a clear loading order and environment-specific settings.

## Key Principles

1. **Flask `app.config` as Source of Truth:** Use Flask's built-in `app.config` dictionary as the primary way to store and access configuration values within the application context.

2. **Environment-specific Configuration:** Support development (`dev`), testing (`test`), and production (`prod`) environments with appropriate default settings for each.

3. **Secure Secret Management:** Keep sensitive information (credentials, API keys) separate from code and protected according to environment needs.

## Implementation Details

### Configuration Loader

A shared configuration loader module (`utils.config_loader.py`) is responsible for:
- Detecting the environment
- Loading base/default settings
- Applying environment-specific overrides
- Loading secrets
- Returning a unified configuration dictionary

```python
# Example implementation in utils/config_loader.py
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

def load_config(env: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from multiple sources in the following order:
    1. Default config values
    2. Environment-specific overrides
    3. Secrets from environment variables or .env file
    4. Command-line arguments (if applicable)
    
    Args:
        env: Optional environment name to override FLASK_ENV.
             Should be one of: 'dev', 'test', 'prod'
    
    Returns a consolidated configuration dictionary.
    """
    config = {}
    
    # 1. Load base settings
    from config.default import config as default_config
    config.update(default_config)
    
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
    if flask_env == "prod":
        from config.prod import config as env_config
    elif flask_env == "test":
        from config.test import config as env_config
    else:  # dev is default
        from config.dev import config as env_config
    
    config.update(env_config)
    
    # 4. Load secrets from environment variables or .env file
    # For production, this could be skipped if using system environment variables
    if flask_env != "prod":
        # Only load .env file in non-production environments
        dotenv_path = os.getenv("DOTENV_PATH", ".env")
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
    
    # 5. Override with environment variables that match config keys
    for key in list(config.keys()):
        env_key = key.upper()  # Environment variables are typically uppercase
        env_val = os.getenv(env_key)
        if env_val is not None:
            # Convert environment values to appropriate types if needed
            config[key] = env_val
    
    # 6. Special handling for database configuration
    if os.getenv("DATABASE_URL"):
        config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    
    return config
```

### Configuration Loading Order

#### Flask Application

In the Flask application factory:

```python
# Example in app/__init__.py or app/app_factory.py
from flask import Flask
from utils.config_loader import load_config

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Load configuration
    config = load_config()
    app.config.from_mapping(config)
    
    # Override with test config if provided
    if test_config:
        app.config.update(test_config)
    
    # Initialize extensions, register blueprints, etc.
    # ...
    
    return app
```

#### Standalone Scripts

For scripts outside the Flask context:

```python
# Example in a standalone script
from utils.config_loader import load_config

config = load_config()

# Use config directly
database_url = config["SQLALCHEMY_DATABASE_URI"]
```

### Environment Detection

- Primary method: `FLASK_ENV` environment variable (`dev`, `test`, `prod`)
- Secondary method: Command-line arguments (optional)

### Secret Management

#### Development Environment

- Local `.env` file (added to `.gitignore`)
- Format: `KEY=VALUE` pairs

#### Test Environment

- Either use a test-specific `.env` file or configure via environment variables in CI/CD system

#### Production Environment (Windows Server)

**Option 1: User Environment Variables (Recommended)**
- Set secrets as Windows environment variables for the specific user account running the Flask application
- Set via Windows System Properties GUI
- Secure and simple for a single-server setup

**Option 2: .env File with NTFS Permissions**
- Create `.env` file outside Git repository (e.g., `C:\ProgramData\CrowbankApp\.env`)
- Apply strict NTFS permissions so only the application's user account can read it
- Load using `python-dotenv` in the configuration loader

### Accessing Configuration

#### Within Flask Context

```python
from flask import current_app

# Example usage
database_url = current_app.config["SQLALCHEMY_DATABASE_URI"]
```

#### Outside Flask Context

```python
from utils.config_loader import load_config

config = load_config()
database_url = config["SQLALCHEMY_DATABASE_URI"]
```

## Configuration Structure

### Base Configuration (config/default.py)

Contains non-sensitive defaults that apply across all environments:

```python
config = {
    "APP_NAME": "Crowbank Intranet",
    "ITEMS_PER_PAGE": 20,
    "UPLOAD_FOLDER": "uploads",
    "ALLOWED_EXTENSIONS": {"pdf", "png", "jpg", "jpeg"},
    "MAX_CONTENT_LENGTH": 16 * 1024 * 1024,  # 16 MB
}
```

### Environment-Specific Configuration

**Development (config/dev.py)**:
```python
config = {
    "DEBUG": True,
    "TESTING": False,
    "SQLALCHEMY_DATABASE_URI": "postgresql://crowbank:password@localhost/crowbank_dev",
    "SQLALCHEMY_TRACK_MODIFICATIONS": True,
}
```

**Testing (config/test.py)**:
```python
config = {
    "DEBUG": True,
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "postgresql://crowbank:password@localhost/crowbank_test",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "WTF_CSRF_ENABLED": False,
}
```

**Production (config/prod.py)**:
```python
config = {
    "DEBUG": False,
    "TESTING": False,
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    # Database URL should come from environment variables in production
}
```

## Alembic Integration

For database migrations with Alembic:

```python
# In migrations/env.py
import os
import sys
from dotenv import load_dotenv

# Add the application root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Use the same configuration loader
from utils.config_loader import load_config

config = load_config()

# Use the database URL from the loaded configuration
from alembic import context
alembic_config = context.config
alembic_config.set_main_option("sqlalchemy.url", config["SQLALCHEMY_DATABASE_URI"])
```

## Implementation Plan

1. Create the configuration directory and files:
   - `config/default.py`
   - `config/dev.py`
   - `config/test.py`
   - `config/prod.py`

2. Implement the `utils/config_loader.py` module

3. Update application initialization to use the new configuration loader

4. Update standalone scripts to use the configuration loader

5. Update Alembic configuration to use the loader

6. Document the approach in the project README

7. Add example `.env` file for development (`.env.example`) 