---
title: configuration
type: guide
status: stable
categories: [guides, configuration]
sub_categories: [settings]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [guide-config-001]
tags: [guide, configuration, settings, yaml]
---

# Configuration Guide

This guide details how to configure the Lattice Lock Framework using environment variables and the `lattice.yaml` configuration file.

## Environment Variables

Lattice Lock uses environment variables for sensitive information and global settings.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `LATTICE_ENV` | Environment mode (`development`, `production`). | `development` |
| `LATTICE_API_KEY` | Global API key for Lattice Cloud (optional). | None |
| `OPENAI_API_KEY` | API key for OpenAI models. | None |
| `ANTHROPIC_API_KEY` | API key for Anthropic models. | None |
| `GOOGLE_API_KEY` | API key for Google Gemini models. | None |

You can set these in your shell or use a `.env` file in your project root.

## Project Configuration (`lattice.yaml`)

Every Lattice Lock project requires a `lattice.yaml` file. This file defines the project structure, models, and validation rules.

### Basic Structure

```yaml
project:
  name: "my-awesome-agent"
  version: "0.1.0"

models:
  default: "gpt-4-turbo"
  fallback: "claude-3-opus"

validation:
  strict_mode: true
  timeout: 30s
```

### Configuration Options

#### `project`
- `name`: (Required) The name of your project.
- `version`: (Required) Semantic version string.
- `authors`: (Optional) List of authors.

#### `models`
Define the models used by your agents.
- `default`: The primary model to use.
- `fallback`: A backup model if the primary fails.
- `local`: Configuration for local models (e.g., Ollama).

#### `validation`
- `strict_mode`: If `true`, warnings are treated as errors.
- `timeout`: Maximum time for validation checks.

## Setting up Providers

### Cloud Providers
To use cloud-based LLMs, ensure you have exported the necessary API keys as environment variables (see above).

### Local Models (Ollama)
Lattice Lock supports local inference via Ollama.

1.  **Install Ollama**: Follow instructions at [ollama.com](https://ollama.com).
2.  **Pull a Model**: `ollama pull llama3`
3.  **Configure `lattice.yaml`**:

    ```yaml
    models:
      default: "ollama/llama3"
    ```

## Database Configuration

If your project uses a database for state management:

```yaml
database:
  type: "sqlite" # or "postgres"
  url: "sqlite:///./lattice.db"
```

For PostgreSQL:
`url: "postgresql://user:password@localhost:5432/lattice"`
