"""
Run the Crowbank Intranet application.

This script runs the Flask development server with the environment
and configuration settings loaded automatically.
"""

import os
import argparse

from app import create_app


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Crowbank Intranet application")
    
    parser.add_argument(
        "--env",
        choices=["dev", "test", "prod"],
        default=None,
        help="Environment to run the application in (overrides FLASK_ENV)",
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to run the application on (default: 0.0.0.0)",
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=5050,
        help="Port to run the application on (default: 5050)",
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run the application in debug mode (overrides config)",
    )
    
    return parser.parse_args()


def main():
    """Run the application."""
    args = parse_args()
    
    # Set environment variable if specified
    if args.env:
        os.environ["FLASK_ENV"] = args.env
    
    # Create the Flask application
    app = create_app()
    
    # Override debug mode if specified
    if args.debug:
        app.debug = True
    
    # Run the application
    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
