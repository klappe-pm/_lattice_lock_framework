---
title: gcp_setup
type: guide
status: stable
categories: [advanced, integration]
sub_categories: [gcp]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [adv-gcp-001]
tags: [advanced, gcp, google_cloud, mcp, setup]
---

# Google Cloud MCP Setup Complete

## ✅ Installed Official Google Cloud MCP Servers

All three official Google Cloud MCP servers from Google have been configured globally across your tools:

1. **@google-cloud/gcloud-mcp** - Interact with Google Cloud via gcloud CLI
2. **@google-cloud/observability-mcp** - Access Google Cloud Observability APIs (logs, metrics, traces)
3. **@google-cloud/storage-mcp** - Interact with Google Cloud Storage

## 📍 Configuration Locations

### Cursor (Global)
- **File**: `~/.cursor/mcp.json`
- **Status**: ✅ Configured

### Claude Desktop
- **File**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Backup**: `~/Library/Application Support/Claude/claude_desktop_config.json.backup`
- **Status**: ✅ Configured (also preserved your existing MCP servers)

### VS Code (Global)
- **File**: `~/Library/Application Support/Code/User/mcp.json`
- **Status**: ✅ Configured

### Warp Terminal
- **File**: `~/Library/Group Containers/2BBY89MBSN.dev.warp/Library/Application Support/dev.warp.Warp-Stable/mcp/mcp.json`
- **Status**: ✅ Configured

## 🔐 Authentication Required

To use these MCP servers, you need to authenticate with Google Cloud:

### Option 1: Install Google Cloud SDK (Recommended)
```bash
brew install --cask google-cloud-sdk
gcloud auth application-default login
```

### Option 2: Use existing credentials
If you have GCP credentials, set the environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
```

## 🚀 Next Steps

1. **Install Google Cloud SDK** (if not already installed)
2. **Authenticate** with `gcloud auth application-default login`
3. **Restart each application** to load the new MCP servers:
   - Restart Claude Desktop
   - Restart Cursor
   - Restart VS Code
   - Restart Warp
4. **Test the servers** by asking the AI assistant to interact with Google Cloud

## 🧰 Available Tools

### gcloud-mcp
- Execute gcloud commands with natural language

### observability-mcp
- List log entries, log names, buckets, views, sinks
- List metric descriptors and time series data
- List alert policies
- Search traces and error groups

### storage-mcp
- List/create/delete buckets
- Read/write/delete objects
- Upload/download files
- Manage bucket metadata and IAM policies
- Execute BigQuery insights queries

## 📚 Documentation

- Official repo: https://github.com/googleapis/gcloud-mcp
- Package names:
  - `@google-cloud/gcloud-mcp`
  - `@google-cloud/observability-mcp`
  - `@google-cloud/storage-mcp`

## 🔒 Security Notes

- MCP permissions are tied to your active gcloud account
- To restrict permissions, use service account impersonation
- Some gcloud commands are restricted by default for safety
- Never share MCP logs without removing sensitive information

## ✨ Usage Examples

Once authenticated, you can use natural language with your AI assistants:

- "List all my GCS buckets"
- "Show me recent errors in my project"
- "Upload this file to my bucket"
- "What are my current Compute Engine instances?"
- "Show me logs from the last hour"
