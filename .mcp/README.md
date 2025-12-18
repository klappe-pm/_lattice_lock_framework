# MCP Configuration for Lattice Lock Framework

> **SECURITY WARNING**
>
> **NEVER put actual API keys, tokens, or secrets in any file in this directory!**
>
> All configurations use environment variables for secrets. The `env` blocks in config files
> specify which environment variables to pass to MCP servers - they do NOT contain actual values.
>
> If you need to store secrets, use:
> - Environment variables in your shell profile
> - A secrets manager (1Password, Bitwarden, etc.)
> - OS keychain (macOS Keychain, Windows Credential Manager)
> - CI/CD secret stores (GitHub Secrets, etc.)

## Overview

This directory contains all MCP (Model Context Protocol) configurations for the Lattice Lock Framework.
Everything is self-contained in this repository - no external dependencies required.

## Directory Structure

```
.mcp/
├── README.md           # This file
├── .env.example        # Template showing required environment variables
├── install.sh          # Installation script for IDE configs
├── config/
│   └── mcp_servers.json    # Master configuration (all servers defined here)
├── templates/
│   ├── cursor-mcp.json         # Ready-to-use Cursor config
│   ├── vscode-mcp.json         # Ready-to-use VS Code config
│   ├── claude-desktop-mcp.json # Ready-to-use Claude Desktop config
│   └── warp-mcp.json           # Ready-to-use Warp Terminal config
└── local/              # Your local overrides (gitignored)
```

## Quick Start

### 1. Set Up Environment Variables

Copy the example and set your API keys in your shell profile:

```bash
# View required variables
cat .mcp/.env.example

# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export BRAVE_API_KEY="your-key-here"
export TAVILY_API_KEY="your-key-here"
# ... etc
```

### 2. Install IDE Configurations

**Option A: Use the install script (recommended)**

```bash
cd .mcp
./install.sh
```

**Option B: Manual copy**

```bash
# Cursor
cp .mcp/templates/cursor-mcp.json ~/.cursor/mcp.json

# VS Code
cp .mcp/templates/vscode-mcp.json ~/Library/Application\ Support/Code/User/mcp.json  # macOS
cp .mcp/templates/vscode-mcp.json ~/.config/Code/User/mcp.json  # Linux

# Claude Desktop
cp .mcp/templates/claude-desktop-mcp.json ~/Library/Application\ Support/Claude/claude_desktop_config.json  # macOS
cp .mcp/templates/claude-desktop-mcp.json ~/.config/Claude/claude_desktop_config.json  # Linux

# Warp Terminal
cp .mcp/templates/warp-mcp.json ~/Library/Group\ Containers/2BBY89MBSN.dev.warp/Library/Application\ Support/dev.warp.Warp-Stable/mcp/mcp.json  # macOS
```

### 3. Authenticate with Cloud Providers

**Google Cloud (for gcloud, observability, storage servers):**

```bash
gcloud auth application-default login
```

**AWS (for aws-api server):**

```bash
aws configure
# Or set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
```

### 4. Restart Your IDE

After installing configs and setting environment variables, restart your IDE to load the MCP servers.

## Available MCP Servers

| Server | Description | Required Env Vars |
|--------|-------------|-------------------|
| `gcloud` | Google Cloud Platform API access | GCP auth |
| `observability` | Google Cloud monitoring and logging | GCP auth |
| `storage` | Google Cloud Storage management | GCP auth |
| `brave-search` | Web search via Brave Search API | `BRAVE_API_KEY` |
| `sequential-thinking` | Extended reasoning capabilities | None |
| `mcp-omnisearch` | Multi-source search (Tavily, Brave, Kagi) | At least one: `TAVILY_API_KEY`, `BRAVE_API_KEY`, `KAGI_API_KEY` |
| `aws-api` | AWS service access and management | AWS credentials |

## Customization

### Adding New Servers

1. Add the server definition to `config/mcp_servers.json`
2. Add the server to each template in `templates/`
3. Update `.env.example` if new environment variables are needed

### Local Overrides

For personal customizations that shouldn't be committed:

1. Create your config in `.mcp/local/` (this directory is gitignored)
2. Copy to your IDE location manually

## Integration with Lattice Lock Orchestrator

The MCP servers provide IDE integration for AI assistants. The Lattice Lock Orchestrator
(Python runtime) uses a separate configuration system based on environment variables.

See `src/lattice_lock_orchestrator/api_clients.py` for the orchestrator's credential requirements:
- `OPENAI_API_KEY` - OpenAI models
- `ANTHROPIC_API_KEY` - Claude models
- `GOOGLE_API_KEY` - Gemini models
- `XAI_API_KEY` - Grok models

**Note:** The Zen MCP Bridge component for runtime MCP integration is planned but not yet implemented.

## Troubleshooting

### MCP servers not loading

1. Check that environment variables are set: `echo $BRAVE_API_KEY`
2. Ensure the config file is in the correct location for your IDE
3. Restart your IDE completely (not just reload)
4. Check IDE logs for MCP-related errors

### Authentication errors

- **Google Cloud**: Run `gcloud auth application-default login`
- **AWS**: Run `aws configure` or set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- **Search APIs**: Verify your API key is valid and has sufficient quota

## Security Best Practices

1. **Never commit secrets** - Use environment variables or secrets managers
2. **Use `.mcp/local/`** - For any personal configs with sensitive data
3. **Rotate keys regularly** - Especially if you suspect exposure
4. **Use least privilege** - Only grant necessary permissions to API keys
5. **Audit access** - Review which MCP servers have access to your credentials
