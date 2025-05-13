"""
Extensions module for the Crowbank Intranet.

This module initializes Flask extensions used throughout the application.
Extensions are initialized in app/__init__.py using init_app().
"""

# Database and ORM
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Migrations
from flask_migrate import Migrate
migrate = Migrate()

# Blueprints and extension instances will be added as needed:
# from flask_login import LoginManager
# login_manager = LoginManager()
#
# from flask_mail import Mail
# mail = Mail()
# 
# etc. 