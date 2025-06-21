#!/usr/bin/env python3
"""
Script to set up MCP servers on the legacy crowbank-flask system.

This script helps install and configure the same MCP servers (except Neon)
on the legacy system for development consistency.
"""

import os
import sys
import json
import shutil
from pathlib import Path

LEGACY_PROJECT_PATH = Path.home() / "crowbank-flask"
CURRENT_PROJECT_PATH = Path(__file__).parent.parent

def main():
    print("🔧 Setting up MCP servers for legacy crowbank-flask system")
    print("=" * 60)
    
    # Check if legacy project exists
    if not LEGACY_PROJECT_PATH.exists():
        print(f"❌ Legacy project not found at {LEGACY_PROJECT_PATH}")
        print("   Please ensure the crowbank-flask project is cloned to ~/crowbank-flask")
        sys.exit(1)
    
    print(f"✅ Found legacy project at {LEGACY_PROJECT_PATH}")
    
    # Create .claude directory if it doesn't exist
    claude_dir = LEGACY_PROJECT_PATH / ".claude"
    claude_dir.mkdir(exist_ok=True)
    print(f"✅ Created .claude directory: {claude_dir}")
    
    # Read current MCP configuration
    current_mcp_config = CURRENT_PROJECT_PATH / ".claude" / "mcp.json"
    
    if not current_mcp_config.exists():
        print(f"❌ Current MCP config not found at {current_mcp_config}")
        sys.exit(1)
    
    with open(current_mcp_config, 'r') as f:
        config = json.load(f)
    
    # Create legacy MCP configuration (exclude Neon)
    legacy_config = {"mcpServers": {}}
    
    for server_name, server_config in config["mcpServers"].items():
        if server_name == "Neon":
            print(f"⏭️  Skipping {server_name} (not needed for legacy system)")
            continue
        
        # Update FileSystem path for legacy system
        if server_name == "FileSystem":
            legacy_server_config = server_config.copy()
            # Update path to legacy project root
            legacy_server_config["args"] = ["-y", "@modelcontextprotocol/server-filesystem", str(LEGACY_PROJECT_PATH)]
            legacy_config["mcpServers"][server_name] = legacy_server_config
            print(f"✅ Configured {server_name} for legacy system path")
        else:
            legacy_config["mcpServers"][server_name] = server_config
            print(f"✅ Added {server_name}")
    
    # Write legacy MCP configuration
    legacy_mcp_config = claude_dir / "mcp.json"
    with open(legacy_mcp_config, 'w') as f:
        json.dump(legacy_config, f, indent=2)
    
    print(f"✅ Created legacy MCP config: {legacy_mcp_config}")
    
    # Copy environment setup script
    current_setup_script = CURRENT_PROJECT_PATH / "scripts" / "setup_mcp_env.py"
    legacy_setup_script = LEGACY_PROJECT_PATH / "scripts" / "setup_mcp_env.py"
    
    # Create scripts directory if it doesn't exist
    (LEGACY_PROJECT_PATH / "scripts").mkdir(exist_ok=True)
    
    if current_setup_script.exists():
        shutil.copy2(current_setup_script, legacy_setup_script)
        print(f"✅ Copied MCP environment setup script to legacy system")
    else:
        print(f"⚠️  MCP environment setup script not found, manual setup required")
    
    print("\n🎯 Setup Complete!")
    print("-" * 40)
    print("Next steps:")
    print("1. Restart Claude Code to activate new MCP servers")
    print("2. Open legacy project (~/crowbank-flask) in Claude Code")
    print("3. MCP servers will be available for legacy system development")
    print("\nConfigured MCP servers for legacy system:")
    for server_name in legacy_config["mcpServers"]:
        print(f"  - {server_name}")

if __name__ == "__main__":
    main()