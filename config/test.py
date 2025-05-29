"""
Testing environment configuration settings for the Crowbank Intranet.
These settings override the default settings when running tests.
"""

config = {
    # Flask settings
    "DEBUG": True,
    "TESTING": True,
    "SERVER_NAME": "localhost",
    
    # Database settings
    "SQLALCHEMY_DATABASE_URI": "postgresql://crowbank:password@localhost/crowbank_test",
    "SQLALCHEMY_ECHO": False,  # Don't log SQL queries in tests
    
    # Testing settings
    "PRESERVE_CONTEXT_ON_EXCEPTION": False,
    "WTF_CSRF_ENABLED": False,  # Disable CSRF protection in tests
    
    # Use in-memory storage for file uploads during tests
    "UPLOAD_FOLDER": "tmp/test_uploads",
    
    # Email testing
    "MAIL_SUPPRESS_SEND": True,  # Don't send actual emails
    
    # Make tests faster
    "BCRYPT_LOG_ROUNDS": 4,  # Lower encryption rounds for faster tests
    "PASSWORD_HASH_METHOD": "plain",  # Use plaintext passwords for tests
}
