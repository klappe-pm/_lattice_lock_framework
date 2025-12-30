# GitHub Authentication Setup Complete

This document describes the GitHub authentication configuration for all projects, IDEs, and MCP servers.

## Summary of Changes

All GitHub authentication issues have been resolved. The system now uses the valid GitHub token stored by the `gh` CLI in your macOS keychain.

## What Was Fixed

### 1. Invalid GITHUB_TOKEN Environment Variable
**Problem:** A placeholder `{{GITHUB_TOKEN}}` was stored in your macOS keychain and loaded by `~/bin/load-keychain-env.sh`, causing `gh auth status` to fail.

**Solution:** Removed the invalid token from the keychain. The `gh` CLI now uses its own valid token (stored separately in the keychain by `gh auth login`).

### 2. SSH Configuration
**Created:** `~/.ssh/config` with GitHub-specific settings to ensure consistent SSH authentication using your `~/.ssh/id_ed25519` key.

### 3. Git Authentication
**Status:** Both SSH and HTTPS authentication methods are now working:
- SSH: Uses `~/.ssh/id_ed25519` key
- HTTPS: Uses `osxkeychain` credential helper with the token from `gh` CLI

### 4. MCP GitHub Server
**Added:** GitHub MCP server (`@modelcontextprotocol/server-github`) to all IDE configurations:
- VS Code: `~/Library/Application Support/Code/User/mcp.json`
- Antigravity: `~/Library/Application Support/Antigravity/User/mcp.json`
- Warp: `~/Library/Group Containers/2BBY89MBSN.dev.warp/Library/Application Support/dev.warp.Warp-Stable/mcp/mcp.json`

**Environment Variable:** Added `GITHUB_PERSONAL_ACCESS_TOKEN` to `~/.mcp_env`, which dynamically retrieves the token from `gh auth token`.

## Current Authentication Status

```bash
✓ gh CLI: Working (using keychain token)
✓ SSH to GitHub: Working (using ~/.ssh/id_ed25519)
✓ HTTPS to GitHub: Working (using osxkeychain)
✓ MCP GitHub Server: Configured (token from gh CLI)
```

## GitHub Token Details

- **Account:** klappe-pm
- **Protocol:** HTTPS
- **Scopes:** 'gist', 'read:org', 'repo'
- **Storage:** macOS Keychain (managed by `gh` CLI)

## How It Works

1. **gh CLI:** Uses token stored in keychain by `gh auth login`
2. **Git HTTPS:** Uses same token via `osxkeychain` credential helper
3. **Git SSH:** Uses `~/.ssh/id_ed25519` key
4. **MCP Servers:** Use `GITHUB_PERSONAL_ACCESS_TOKEN` from `~/.mcp_env`, which calls `gh auth token`

## MCP GitHub Server Usage

The GitHub MCP server provides AI assistants with:
- Repository management (list, create, search)
- Issue and PR operations
- Code search
- Branch and commit operations

### Environment Setup

The token is automatically loaded when you source `~/.mcp_env` (already done in `~/.bashrc`):

```bash
source ~/.mcp_env
```

This sets `GITHUB_PERSONAL_ACCESS_TOKEN` by calling `gh auth token`.

### IDE Configuration

All three IDEs (VS Code, Antigravity, Warp) have the GitHub MCP server configured:

```json
"github": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
  }
}
```

## Verification

Test your setup:

```bash
# Test gh CLI
gh auth status

# Test git SSH
ssh -T git@github.com

# Test git HTTPS
git fetch --dry-run

# Test MCP environment variable
source ~/.mcp_env && echo $GITHUB_PERSONAL_ACCESS_TOKEN | cut -c1-20
```

All commands should succeed without errors.

## Troubleshooting

### gh CLI Issues
If `gh auth status` shows errors, re-authenticate:
```bash
gh auth login
```

### SSH Issues
Verify SSH key is loaded:
```bash
ssh-add -l
```

If not, add it:
```bash
ssh-add ~/.ssh/id_ed25519
```

### MCP Server Issues
If MCP servers can't access GitHub:
1. Verify token is set: `echo $GITHUB_PERSONAL_ACCESS_TOKEN`
2. Restart your IDE to reload MCP configurations
3. Check IDE logs for MCP-related errors

### Token Expiration
If your token expires:
1. Run `gh auth refresh`
2. Restart your IDEs to pick up the new token

## Security Notes

- ✓ No tokens stored in plain text files
- ✓ Token managed securely by macOS Keychain
- ✓ MCP servers access token via environment variable only
- ✓ SSH key protected by macOS Keychain (`UseKeychain yes`)

## Files Modified

1. Removed: Invalid `GITHUB_TOKEN` from macOS keychain
2. Created: `~/.ssh/config`
3. Updated: `~/.mcp_env`
4. Updated: All IDE MCP configurations (VS Code, Antigravity, Warp)
5. Updated: MCP templates in `.mcp/templates/`
6. Updated: `.mcp/config/mcp_servers.json`

## Next Steps

- Restart your IDEs (VS Code, Antigravity, Warp) to load the new MCP GitHub server
- Test GitHub operations in each IDE using AI assistants
- Monitor MCP server logs if you encounter issues

---

**Date:** 2025-12-27
**System:** macOS
**Account:** klappe-pm
