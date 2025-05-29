"""
Production environment configuration settings for the Crowbank Intranet.
These settings override the default settings when running in production mode.
"""

config = {
    # Flask settings
    "DEBUG": False,
    "TESTING": False,
    
    # Production security settings
    "SESSION_COOKIE_SECURE": True,
    "SESSION_COOKIE_HTTPONLY": True,
    "REMEMBER_COOKIE_SECURE": True,
    "REMEMBER_COOKIE_HTTPONLY": True,
    
    # Production performance settings
    "SQLALCHEMY_ECHO": False,
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SQLALCHEMY_ENGINE_OPTIONS": {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    },
    
    # Caching
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    
    # Logging
    "LOG_LEVEL": "ERROR",
    
    # Email error reporting
    "MAIL_ERROR_RECIPIENT": "admin@crowbank.co.uk",
}
