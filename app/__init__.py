"""
Crowbank Intranet - Flask Application Factory
"""

import os
from datetime import datetime
from flask import Flask, render_template

from app.utils.config_loader import load_config
from app.extensions import db, migrate


def create_app(test_config=None):
    """
    Create and configure the Flask application.
    
    Args:
        test_config: Configuration to use for testing (overrides loaded config)
        
    Returns:
        The configured Flask application
    """
    # Create Flask app instance
    app = Flask(__name__, 
                instance_relative_config=True,
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    config = load_config()
    app.config.from_mapping(config)
    
    # Override with test config if provided
    if test_config:
        app.config.update(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Register extensions
    _register_extensions(app)
    
    # Register blueprints
    # _register_blueprints(app)
    
    # Register error handlers
    # _register_error_handlers(app)
    
    # Register shell context
    _register_shell_context(app)
    
    # Register CLI commands
    # _register_commands(app)
    
    # Register template context
    _register_template_context(app)
    
    # Home route
    @app.route('/')
    def home():
        return render_template('home.html')
    
    return app


def _register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)


def _register_blueprints(app):
    """Register Flask blueprints."""
    # from app.routes.auth import auth_bp
    # from app.routes.booking import booking_bp
    # app.register_blueprint(auth_bp)
    # app.register_blueprint(booking_bp)
    pass


def _register_error_handlers(app):
    """Register error handlers."""
    # @app.errorhandler(404)
    # def page_not_found(error):
    #     return render_template('errors/404.html'), 404
    pass


def _register_shell_context(app):
    """Register shell context objects."""
    @app.shell_context_processor
    def make_shell_context():
        return {'app': app, 'db': db}


def _register_commands(app):
    """Register CLI commands."""
    # @app.cli.command("init-db")
    # def init_db_command():
    #     """Initialize the database."""
    #     db.create_all()
    #     click.echo("Initialized the database.")
    pass


def _register_template_context(app):
    """Register template context processors."""
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()} 