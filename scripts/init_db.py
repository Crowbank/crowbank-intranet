#!/usr/bin/env python
"""
Database initialization script for Crowbank Intranet.

This script creates all database tables based on the SQLAlchemy models.
It should be run once to set up the database schema.
"""

import os
import sys

# Add the project root directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db


def init_db():
    """Initialize the database, creating all tables."""
    app = create_app()
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully.")

