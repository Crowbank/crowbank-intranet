"""
Development environment configuration settings for the Crowbank Intranet.
These settings override the default settings when running in development mode.
"""

config = {
    # Flask settings
    "DEBUG": True,
    "TESTING": False,
    
    # Database settings (with placeholder password that will be overridden)
    "SQLALCHEMY_DATABASE_URI": "postgresql://crowbank:password@localhost/crowbank",
    "SQLALCHEMY_ECHO": True,  # Log SQL queries
    
    # Logging
    "LOG_LEVEL": "DEBUG",
    
    # Development-specific settings
    "SEND_FILE_MAX_AGE_DEFAULT": 0,  # Disable caching for static files
    "TEMPLATES_AUTO_RELOAD": True,   # Auto-reload templates
    
    # Debugging tools
    "DEBUG_TB_ENABLED": True,        # Enable Flask-DebugToolbar
    "DEBUG_TB_INTERCEPT_REDIRECTS": False,
}
