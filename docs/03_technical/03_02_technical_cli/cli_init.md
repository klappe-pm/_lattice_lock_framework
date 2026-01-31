---
title: Init CLI
type: reference
status: stable
categories:
  - Technical
  - CLI
sub_categories:
  - Setup
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids:
  - cli-init-001
tags:
  - init
  - cli
  - setup
---

# lattice-lock init

Initialize a new Lattice Lock project with scaffolding.

## Synopsis

```bash
lattice-lock init [OPTIONS] PROJECT_NAME
```

## Description

The `init` command creates a new project directory with a compliant structure for the Lattice Lock Framework. It generates configuration files, directory layouts, and starter templates based on the selected project type.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `PROJECT_NAME` | Yes | Name of the project to create. Must be in snake_case format (lowercase letters, numbers, underscores) and start with a letter. |

## Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--template` | `-t` | choice | `service` | Project template type. Choices: `agent`, `service`, `library` |
| `--output-dir` | `-o` | path | `.` | Output directory for the project |
| `--ci` | | choice | `github` | CI/CD provider. Choices: `github`, `aws` |

## Project Templates

### service (default)

Creates a service-oriented project structure suitable for APIs, microservices, and backend applications.

**Generated structure:**
```
my_project/
├── .github/
│   └── workflows/
│       └── lattice-lock.yml
├── src/
│   ├── __init__.py
│   ├── shared/
│   │   └── __init__.py
│   └── services/
│       ├── __init__.py
│       └── my_project.py
├── tests/
│   └── test_contracts.py
├── .gitignore
├── lattice.yaml
└── README.md
```

### agent

Creates an AI agent project with agent definition files.

**Generated structure:**
```
my_agent/
├── .github/
│   └── workflows/
│       └── lattice-lock.yml
├── src/
│   ├── __init__.py
│   ├── shared/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
├── tests/
│   └── test_contracts.py
├── .gitignore
├── agent.yaml
├── lattice.yaml
└── README.md
```

### library

Creates a reusable library project structure.

**Generated structure:**
```
my_library/
├── .github/
│   └── workflows/
│       └── lattice-lock.yml
├── src/
│   ├── __init__.py
│   ├── my_library/
│   │   └── __init__.py
│   ├── shared/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
├── tests/
│   └── test_contracts.py
├── .gitignore
├── lattice.yaml
└── README.md
```

## CI/CD Providers

### github (default)

Generates GitHub Actions workflow files in `.github/workflows/`.

### aws

Generates AWS CodeBuild configuration in `ci/aws/`:
- `buildspec.yml` - AWS CodeBuild build specification
- `pipeline.yml` - AWS CodePipeline definition
- `codebuild-project.yml` - CodeBuild project configuration

## Examples

### Basic Usage

Create a service project in the current directory:

```bash
lattice-lock init my_api_service
```

### Specify Template Type

Create an agent project:

```bash
lattice-lock init my_ai_agent --template agent
```

Create a library project:

```bash
lattice-lock init my_utils_lib --template library
```

### Custom Output Directory

Create project in a specific location:

```bash
lattice-lock init my_project --output-dir ~/projects/
```

### AWS CI/CD

Create project with AWS CodeBuild/CodePipeline support:

```bash
lattice-lock init my_service --ci aws
```

### Verbose Output

See detailed creation progress:

```bash
lattice-lock -v init my_project
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Project created successfully |
| `1` | Error - invalid project name, directory already exists, or creation failed |

## Project Name Validation

Project names must follow these rules:
- Must be in snake_case format
- Must start with a letter (a-z)
- Can contain lowercase letters, numbers, and underscores
- Cannot contain spaces, hyphens, or uppercase letters

**Valid names:**
- `my_project`
- `api_v2`
- `data_processor_2024`

**Invalid names:**
- `MyProject` (uppercase)
- `my-project` (hyphens)
- `2nd_project` (starts with number)
- `my project` (spaces)

## Post-Creation Steps

After creating a project, the command displays recommended next steps:

```
Next steps:
  cd my_project
  python -m venv .venv
  source .venv/bin/activate
  pip install lattice-lock
  lattice-lock validate
```

## See Also

- [CLI Overview](docs/reference/cli/index.md)
- [validate](validate.md) - Validate the created project
- [Configuration Reference](docs/reference/configuration.md) - Customize lattice.yaml
