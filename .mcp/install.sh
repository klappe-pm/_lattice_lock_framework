#!/bin/bash
# MCP Configuration Installer for Lattice Lock Framework
# This script copies MCP configurations to your IDE locations
#
# SECURITY NOTE: This script does NOT handle secrets.
# You must set environment variables separately (see .env.example)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/templates"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}MCP Configuration Installer${NC}"
echo -e "${BLUE}Lattice Lock Framework${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
fi

echo -e "${YELLOW}Detected OS: $OS${NC}"
echo ""

# Define target paths based on OS
CURSOR_PATH=""
VSCODE_PATH=""
CLAUDE_PATH=""
WARP_PATH=""

if [[ "$OS" == "macos" ]]; then
    CURSOR_PATH="$HOME/.cursor/mcp.json"
    VSCODE_PATH="$HOME/Library/Application Support/Code/User/mcp.json"
    CLAUDE_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
    WARP_PATH="$HOME/Library/Group Containers/2BBY89MBSN.dev.warp/Library/Application Support/dev.warp.Warp-Stable/mcp/mcp.json"
elif [[ "$OS" == "linux" ]]; then
    CURSOR_PATH="$HOME/.cursor/mcp.json"
    VSCODE_PATH="$HOME/.config/Code/User/mcp.json"
    CLAUDE_PATH="$HOME/.config/Claude/claude_desktop_config.json"
    WARP_PATH="$HOME/.config/warp/mcp.json"
else
    echo -e "${RED}Windows detected. Please manually copy configs from:${NC}"
    echo -e "  $TEMPLATES_DIR/"
    echo -e "${YELLOW}To your IDE configuration directories:${NC}"
    echo -e "  Cursor: %APPDATA%\\Cursor\\mcp.json"
    echo -e "  VS Code: %APPDATA%\\Code\\User\\mcp.json"
    echo -e "  Claude Desktop: %APPDATA%\\Claude\\claude_desktop_config.json"
    exit 0
fi

# Function to install config
install_config() {
    local name="$1"
    local source="$2"
    local target="$3"
    
    if [[ ! -f "$source" ]]; then
        echo -e "${RED}Source file not found: $source${NC}"
        return 1
    fi
    
    # Create target directory if it doesn't exist
    local target_dir=$(dirname "$target")
    if [[ ! -d "$target_dir" ]]; then
        echo -e "${YELLOW}Creating directory: $target_dir${NC}"
        mkdir -p "$target_dir"
    fi
    
    # Backup existing config if it exists
    if [[ -f "$target" ]]; then
        local backup="${target}.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}Backing up existing config to: $backup${NC}"
        cp "$target" "$backup"
    fi
    
    # Copy the config
    cp "$source" "$target"
    echo -e "${GREEN}Installed $name config to: $target${NC}"
}

# Menu
echo "Select which IDE configs to install:"
echo "  1) Cursor"
echo "  2) VS Code"
echo "  3) Claude Desktop"
echo "  4) Warp Terminal"
echo "  5) All"
echo "  6) Exit"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        install_config "Cursor" "$TEMPLATES_DIR/cursor-mcp.json" "$CURSOR_PATH"
        ;;
    2)
        install_config "VS Code" "$TEMPLATES_DIR/vscode-mcp.json" "$VSCODE_PATH"
        ;;
    3)
        install_config "Claude Desktop" "$TEMPLATES_DIR/claude-desktop-mcp.json" "$CLAUDE_PATH"
        ;;
    4)
        install_config "Warp" "$TEMPLATES_DIR/warp-mcp.json" "$WARP_PATH"
        ;;
    5)
        install_config "Cursor" "$TEMPLATES_DIR/cursor-mcp.json" "$CURSOR_PATH"
        install_config "VS Code" "$TEMPLATES_DIR/vscode-mcp.json" "$VSCODE_PATH"
        install_config "Claude Desktop" "$TEMPLATES_DIR/claude-desktop-mcp.json" "$CLAUDE_PATH"
        install_config "Warp" "$TEMPLATES_DIR/warp-mcp.json" "$WARP_PATH"
        ;;
    6)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installation complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}IMPORTANT: Don't forget to set your environment variables!${NC}"
echo -e "See .env.example for required variables."
echo ""
echo -e "${YELLOW}Required for some MCP servers:${NC}"
echo "  - BRAVE_API_KEY (for brave-search, mcp-omnisearch)"
echo "  - TAVILY_API_KEY (for mcp-omnisearch)"
echo "  - KAGI_API_KEY (for mcp-omnisearch)"
echo ""
echo -e "${YELLOW}For Google Cloud servers:${NC}"
echo "  Run: gcloud auth application-default login"
echo ""
echo -e "${YELLOW}Restart your IDE to load the new configuration.${NC}"
