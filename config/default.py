"""
Default configuration settings for the Crowbank Intranet.
These are the base settings used across all environments.
"""

config = {
    # Application settings
    "APP_NAME": "Crowbank Intranet",
    "APP_VERSION": "0.1.0",
    
    # UI settings
    "ITEMS_PER_PAGE": 20,
    "MAX_SEARCH_RESULTS": 100,
    
    # File handling
    "UPLOAD_FOLDER": "uploads",
    "ALLOWED_EXTENSIONS": {"pdf", "png", "jpg", "jpeg", "docx", "xlsx"},
    "MAX_CONTENT_LENGTH": 16 * 1024 * 1024,  # 16 MB
    
    # Session settings
    "PERMANENT_SESSION_LIFETIME": 86400,  # 24 hours in seconds
    "SESSION_TYPE": "filesystem",
    
    # Email settings (non-sensitive defaults)
    "MAIL_SERVER": "smtp.example.com",
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_DEFAULT_SENDER": "intranet@crowbank.co.uk",
    
    # Logging
    "LOG_LEVEL": "INFO",
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    
    # SQLAlchemy
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
}
