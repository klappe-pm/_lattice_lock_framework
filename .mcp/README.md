# MCP Configuration for Lattice Lock Framework

This project uses centralized MCP configurations from the `llm_configurations` repository.

## Location

Configurations are managed at:
```
/Users/kevinlappe/Documents/llm_configurations
```

## Usage

### Load MCP Configurations

The MCP configurations are automatically generated from a single source of truth:

```bash
# Navigate to the configurations repository
cd /Users/kevinlappe/Documents/llm_configurations

# Generate all IDE-specific configurations
python3 generate_mcp_configs.py

# Install to your IDE (examples)
cp mcp/cursor-mcp.json ~/.cursor/mcp.json
cp mcp/warp-mcp.json ~/.warp/mcp_config.json
```

### Available MCP Servers

All configurations include these MCP servers:
- **gcloud** - Google Cloud Platform API access
- **observability** - Google Cloud monitoring and logging
- **storage** - Google Cloud Storage management
- **brave-search** - Web search via Brave Search API
- **sequential-thinking** - Extended reasoning capabilities
- **mcp-omnisearch** - Multi-source search (Tavily, Brave, Kagi)
- **aws-api** - AWS service access and management

### Load Credentials

**IMPORTANT:** Before using any MCP servers, load your API credentials:

```bash
eval "$(load-keychain-credentials)"
```

This loads all API keys from macOS Keychain into environment variables.

## Adding New MCP Servers

To add new MCP servers for this project:

1. Edit `/Users/kevinlappe/Documents/llm_configurations/mcp_config_main.json`
2. Run `python3 generate_mcp_configs.py`
3. Reinstall configs to your IDEs

## Documentation

Full documentation available at:
- [MCP Configuration System](../../llm_configurations/MCP_CONFIG_SYSTEM.md)
- [Quick Reference](../../llm_configurations/QUICK_REFERENCE.md)

## Security

- API keys stored in macOS Keychain only
- Configuration files use `${ENV_VAR}` references
- Never commit actual API keys to version control
- Load credentials with `eval "$(load-keychain-credentials)"` before starting IDEs

## Integration with Lattice Lock

The Lattice Lock Framework's Zen MCP Bridge component can leverage these MCP servers for:
- Multi-model orchestration
- Enhanced reasoning capabilities
- Cloud resource management
- Web search and research capabilities

See `src/lattice_lock_orchestrator/zen_mcp_bridge.py` for integration details.
