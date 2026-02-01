---
title: ide_integration
type: guide
status: stable
categories: [guides, integration]
sub_categories: [ide]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [guide-ide-001]
tags: [guide, ide, integration, claude_code, mcp]
---

# IDE Integration Guide

This guide explains how to integrate Lattice Lock's MCP server with popular IDEs and AI coding assistants.

## Claude Code

To use Lattice Lock with Claude Code, you need to configure the MCP server in your Claude Code settings.

1.  **Install Lattice Lock**: Ensure `lattice-lock` is installed in your python environment.
2.  **Configure MCP**:
    Add the following to your MCP configuration (usually `~/.claude/mcp.json` or similar):

    ```json
    {
      "mcpServers": {
        "lattice-lock": {
          "command": "lattice",
          "args": ["mcp"]
        }
      }
    }
    ```

3.  **Verify**: Restart Claude Code and verify that `validate_code` and `ask_orchestrator` tools are available.

## Cursor

Cursor supports MCP native integration.

1.  Open Cursor Settings.
2.  Navigate to **Features** > **MCP**.
3.  Click **Add New MCP Server**.
4.  Enter Name: `lattice-lock`.
5.  Select Type: `stdio`.
6.  Command: `lattice` (or full path to your `lattice` executable if not in PATH).
7.  Args: `mcp`.

## VS Code

Using the official MCP extension for VS Code:

1.  Install the **Model Context Protocol** extension.
2.  Open your VS Code `settings.json`.
3.  Add the server configuration:

    ```json
    "mcp.servers": {
        "lattice-lock": {
            "command": "lattice",
            "args": ["mcp"],
            "transport": "stdio"
        }
    }
    ```

## Troubleshooting

-   **Command not found**: Use the absolute path to your python environment's `lattice` command (e.g., `/Users/username/venv/bin/lattice`).
-   **Connection refused**: Ensure you are using `stdio` transport as `sse` is not yet fully supported.
-   **Feature disabled**: Check `LATTICE_DISABLED_FEATURES` env var. Ensure `mcp` is not in the list.
