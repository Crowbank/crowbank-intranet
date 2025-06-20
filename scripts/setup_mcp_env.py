#!/usr/bin/env python3
"""
Script to set up environment variables for MCP servers from YAML configuration.

This script reads the secret.yaml file and sets the appropriate environment
variables that the MCP servers expect.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.utils.yaml_config import load_config


def setup_mcp_environment():
    """Set up environment variables for MCP servers from YAML config."""
    try:
        config = load_config()
        nested_config = config["nested"]
        
        # Extract MCP credentials
        mcp_config = nested_config.get("mcp", {})
        
        # AWS/Cloudflare R2 credentials
        aws_config = mcp_config.get("aws", {})
        if aws_config.get("access_key_id"):
            os.environ["AWS_ACCESS_KEY_ID"] = aws_config["access_key_id"]
        if aws_config.get("secret_access_key"):
            os.environ["AWS_SECRET_ACCESS_KEY"] = aws_config["secret_access_key"]
        if aws_config.get("endpoint_url"):
            os.environ["AWS_ENDPOINT_URL"] = aws_config["endpoint_url"]
        if aws_config.get("region"):
            os.environ["AWS_REGION"] = aws_config["region"]
            
        # GitHub credentials
        github_config = mcp_config.get("github", {})
        if github_config.get("personal_access_token"):
            os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"] = github_config["personal_access_token"]
            
        print("✅ MCP environment variables set up successfully")
        print("Environment variables configured:")
        
        if "AWS_ACCESS_KEY_ID" in os.environ:
            print(f"  - AWS_ACCESS_KEY_ID: {os.environ['AWS_ACCESS_KEY_ID'][:8]}...")
        if "AWS_SECRET_ACCESS_KEY" in os.environ:
            print("  - AWS_SECRET_ACCESS_KEY: [HIDDEN]")
        if "AWS_ENDPOINT_URL" in os.environ:
            print(f"  - AWS_ENDPOINT_URL: {os.environ['AWS_ENDPOINT_URL']}")
        if "AWS_REGION" in os.environ:
            print(f"  - AWS_REGION: {os.environ['AWS_REGION']}")
        if "GITHUB_PERSONAL_ACCESS_TOKEN" in os.environ:
            print(f"  - GITHUB_PERSONAL_ACCESS_TOKEN: {os.environ['GITHUB_PERSONAL_ACCESS_TOKEN'][:8]}...")
            
    except Exception as e:
        print(f"❌ Error setting up MCP environment: {e}")
        sys.exit(1)


def generate_env_file():
    """Generate a .env file with MCP credentials for shell use."""
    try:
        config = load_config()
        nested_config = config["nested"]
        mcp_config = nested_config.get("mcp", {})
        
        env_content = "# MCP Environment Variables (Generated from secret.yaml)\n"
        env_content += "# Source this file or use with python-dotenv\n\n"
        
        # AWS/Cloudflare R2 credentials
        aws_config = mcp_config.get("aws", {})
        if aws_config.get("access_key_id"):
            env_content += f'export AWS_ACCESS_KEY_ID="{aws_config["access_key_id"]}"\n'
        if aws_config.get("secret_access_key"):
            env_content += f'export AWS_SECRET_ACCESS_KEY="{aws_config["secret_access_key"]}"\n'
        if aws_config.get("endpoint_url"):
            env_content += f'export AWS_ENDPOINT_URL="{aws_config["endpoint_url"]}"\n'
        if aws_config.get("region"):
            env_content += f'export AWS_REGION="{aws_config["region"]}"\n'
            
        env_content += "\n"
        
        # GitHub credentials
        github_config = mcp_config.get("github", {})
        if github_config.get("personal_access_token"):
            env_content += f'export GITHUB_PERSONAL_ACCESS_TOKEN="{github_config["personal_access_token"]}"\n'
            
        # Write to .env.mcp file
        env_file = project_root / ".env.mcp"
        with open(env_file, "w") as f:
            f.write(env_content)
            
        print(f"✅ Generated MCP environment file: {env_file}")
        print("To use in shell: source .env.mcp")
        
    except Exception as e:
        print(f"❌ Error generating MCP .env file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Set up MCP environment variables")
    parser.add_argument("--generate-env", action="store_true", 
                       help="Generate .env.mcp file instead of setting environment")
    
    args = parser.parse_args()
    
    if args.generate_env:
        generate_env_file()
    else:
        setup_mcp_environment()