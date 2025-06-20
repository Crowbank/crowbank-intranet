# Configuration Management

This document outlines the configuration management strategy for the Crowbank Intranet system.

## Overview

The Crowbank Intranet application uses a YAML-based configuration management approach with Flask's native configuration system, providing a clear loading order and environment-specific settings.

## Key Principles

1. **Flask `app.config` as Source of Truth:** Use Flask's built-in `app.config` dictionary as the primary way to store and access configuration values within the application context.

2. **Environment-specific Configuration:** Support development (`dev`), testing (`test`), and production (`prod`) environments with appropriate default settings for each.

3. **Secure Secret Management:** Keep sensitive information (credentials, API keys) separate from code and protected according to environment needs.

## Implementation Details

### Configuration Loader

A shared YAML configuration loader module (`app/utils/yaml_config.py`) is responsible for:
- Detecting the environment
- Loading base/default settings from YAML files
- Applying environment-specific overrides
- Loading secrets from separate YAML files
- Returning both nested and flattened configuration dictionaries

```python
# Example implementation in app/utils/yaml_config.py
import os
import yaml
from typing import Dict, Any, Optional

def load_config(env: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML files in the following order:
    1. Default config values (config/yaml/default.yaml)
    2. Environment-specific overrides (config/yaml/dev.yaml, etc.)
    3. Secret config values (config/yaml/secret.yaml)
    
    Args:
        env: Optional environment name to override FLASK_ENV.
             Should be one of: 'dev', 'test', 'prod'
    
    Returns a dictionary with both nested and flattened configurations.
    """
    # Base config directory
    config_dir = os.path.join(os.getcwd(), "config", "yaml")
    
    # 1. Determine environment
    flask_env = env or os.getenv("FLASK_ENV", "dev")
    
    # 2. Load default config
    default_config_path = os.path.join(config_dir, "default.yaml")
    config = load_yaml_file(default_config_path)
    
    # 3. Load environment-specific config
    env_config_path = os.path.join(config_dir, f"{flask_env}.yaml")
    env_config = load_yaml_file(env_config_path)
    config = deep_merge(env_config, config)
    
    # 4. Load secret config (if exists)
    secret_config_path = os.path.join(config_dir, "secret.yaml")
    secret_config = load_yaml_file(secret_config_path)
    config = deep_merge(secret_config, config)
    
    # 5. Create Flask-compatible flattened config
    flask_config = flatten_dict(config)
    
    return {
        "nested": config,      # Original nested structure
        "flat": flask_config,  # Flattened for Flask compatibility
    }
```

### Configuration Loading Order

#### Flask Application

In the Flask application factory:

```python
# Example in app/__init__.py
from flask import Flask
from app.utils.yaml_config import load_config

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Load configuration from YAML files
    config = load_config()
    
    # Apply the flattened config to Flask
    app.config.from_mapping(config["flat"])
    
    # Make nested config available as well
    app.config["CONFIG"] = config["nested"]
    
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
from app.utils.yaml_config import load_config

config = load_config()

# Use nested config for complex structures
database_config = config["nested"]["database"]

# Use flattened config for Flask-compatible keys
database_url = config["flat"]["SQLALCHEMY_DATABASE_URI"]
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

### Base Configuration (config/yaml/default.yaml)

Contains non-sensitive defaults that apply across all environments:

```yaml
# Application settings
app:
  name: "Crowbank Intranet"
  version: "0.1.0"

# UI settings  
ui:
  items_per_page: 20
  max_search_results: 100

# File handling
files:
  upload_folder: "uploads"
  allowed_extensions: ["pdf", "png", "jpg", "jpeg", "docx", "xlsx"]
  max_content_length: 16777216  # 16 MB

# Session settings
session:
  permanent_session_lifetime: 86400  # 24 hours
  type: "filesystem"
```

### Environment-Specific Configuration

**Development (config/yaml/dev.yaml)**:
```yaml
# Flask settings
flask:
  debug: true
  testing: false

# Database settings (credentials in secret.yaml)
database:
  host: "192.168.0.201"
  port: 54320
  name: "crowbank"

# SQLAlchemy settings
sqlalchemy:
  echo: true
  track_modifications: true

# Development-specific settings
development:
  send_file_max_age: 0
  templates_auto_reload: true
```

**Testing (config/yaml/test.yaml)**:
```yaml
flask:
  debug: true
  testing: true

database:
  host: "localhost"
  port: 5432
  name: "crowbank_test"

sqlalchemy:
  track_modifications: false
  
# Disable CSRF for testing
wtf:
  csrf_enabled: false
```

**Production (config/yaml/prod.yaml)**:
```yaml
flask:
  debug: false
  testing: false

sqlalchemy:
  track_modifications: false
  echo: false

# Production-specific settings
production:
  send_file_max_age: 31536000  # 1 year
```

### Secret Configuration (config/yaml/secret.yaml)

Contains sensitive information (not committed to git):

```yaml
# Database credentials
database:
  user: "crowbank"
  password: "your_secure_password"

# Legacy database credentials  
legacy_database:
  username: "PA"
  password: "legacy_password"

# Cloud storage credentials
cloud_storage:
  access_key_id: "your_access_key"
  secret_access_key: "your_secret_key"

# Email credentials
email:
  username: "your_email@crowbank.co.uk"
  password: "your_email_password"
```

## Alembic Integration

For database migrations with Alembic:

```python
# In migrations/env.py
import os
import sys

# Add the application root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Use the YAML configuration loader
from app.utils.yaml_config import load_config

config = load_config()

# Use the database URL from the loaded configuration
from alembic import context
alembic_config = context.config
alembic_config.set_main_option("sqlalchemy.url", config["flat"]["SQLALCHEMY_DATABASE_URI"])
```

## Implementation Status

✅ **Completed**:
- YAML configuration directory and files created
- `app/utils/yaml_config.py` module implemented
- Application initialization updated to use YAML configuration
- Migration scripts updated to use YAML configuration
- Documentation updated to reflect YAML approach

📝 **Configuration Files**:
- `config/yaml/default.yaml` - Base configuration
- `config/yaml/dev.yaml` - Development overrides  
- `config/yaml/test.yaml` - Testing overrides
- `config/yaml/prod.yaml` - Production overrides
- `config/yaml/secret.yaml` - Sensitive credentials (not in git)

🔧 **Usage**:
- Flask app: Uses `app.utils.yaml_config.load_config()`
- Migration scripts: Uses same loader for database connections
- Environment detection: `FLASK_ENV` environment variable 