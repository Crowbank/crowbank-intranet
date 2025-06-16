#!/bin/bash
# Development helper script using uv

set -e

# Ensure uv is available
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  install     Install/sync dependencies"
    echo "  lint        Run ruff linting"
    echo "  format      Format code with ruff"
    echo "  check       Run type checking with mypy"
    echo "  test        Run tests with pytest"
    echo "  dev         Start development server"
    echo "  shell       Start Flask shell"
    echo "  migrate     Run database migrations"
    echo "  help        Show this help message"
}

# Main command dispatcher
case "${1:-help}" in
    install)
        echo "Installing dependencies..."
        uv sync
        ;;
    lint)
        echo "Running linting..."
        uv run ruff check app/ "${@:2}"
        ;;
    format)
        echo "Formatting code..."
        uv run ruff format app/
        ;;
    check)
        echo "Running type checks..."
        uv run mypy app/
        ;;
    test)
        echo "Running tests..."
        uv run pytest "${@:2}"
        ;;
    dev)
        echo "Starting development server..."
        uv run flask run --debug
        ;;
    shell)
        echo "Starting Flask shell..."
        uv run flask shell
        ;;
    migrate)
        echo "Running database migrations..."
        uv run flask db upgrade
        ;;
    help)
        show_usage
        ;;
    *)
        echo "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac