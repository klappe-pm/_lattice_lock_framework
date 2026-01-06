---
title: "Compile CLI"
type: reference
status: stable
categories: [Technical, CLI]
sub_categories: [Compiler]
date_created: 2024-12-10
date_revised: 2026-01-06
file_ids: [cli-compile-001]
tags: [compile, cli, build]
author: Compiler Agent
---

# Compile Command

The `compile` command validates the project against the `lattice.yaml` specification and generates enforced code structures.

## Usage

```bash
lattice-lock compile [OPTIONS]
```

## Description

The compiler reads the `lattice.yaml` file in the project root and enforces governance rules, ensuring that the implementation matches the specified architecture and constraints.

## Options

- `--watch`: Watch for changes in `lattice.yaml` and recompile automatically.
- `--verbose`: Enable verbose output.
