---
title: Admin CLI
type: reference
status: stable
categories:
  - Technical
  - CLI
sub_categories:
  - Admin
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids:
  - cli-admin-001
tags:
  - admin
  - cli
  - tools
---

# Admin Command

The `admin` command allows management of users, API keys, and system configuration.

## Usage

```bash
lattice-lock admin [COMMAND] [OPTIONS]
```

## Commands

### `user`

Manage system users.

```bash
# Create a new user
lattice-lock admin user create --username alice --role developer

# Reset password
lattice-lock admin user reset-password --username alice
```

### `apikey`

Manage API keys.

```bash
# specific key generation
lattice-lock admin apikey create --name "ci-runner" --role operator
```

### `config`

View or update system configuration.

```bash
lattice-lock admin config show
```
