"""
Development environment configuration settings for the Crowbank Intranet.
These settings override the default settings when running in development mode.
"""

config = {
    # Flask settings
    "DEBUG": True,
    "TESTING": False,
    
    # Database URI will be loaded from YAML configuration
    # SQLAlchemy echo setting will be loaded from YAML configuration
    
    # Logging
    "LOG_LEVEL": "DEBUG",
    
    # Development-specific settings
    "SEND_FILE_MAX_AGE_DEFAULT": 0,  # Disable caching for static files
    "TEMPLATES_AUTO_RELOAD": True,   # Auto-reload templates
    
    # Debugging tools
    "DEBUG_TB_ENABLED": True,        # Enable Flask-DebugToolbar
    "DEBUG_TB_INTERCEPT_REDIRECTS": False,
} 