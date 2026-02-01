---
title: interactive_onboarding
type: tutorial
status: stable
categories: [tutorials, getting_started]
sub_categories: [onboarding]
date_created: 2025-10-05
date_revised: 2026-01-31
file_ids: [tut-onboarding-001]
tags: [tutorial, onboarding, getting_started, beginner]
---

# Interactive Onboarding Guide

Welcome to **Lattice Lock**! This guide will take you from zero to your first successful project validation in under 10 minutes.

---

## What You're About to Learn

By the end of this guide, you will:

- Understand what Lattice Lock does and why it matters
- Complete your first successful schema validation
- Know how to use the CLI commands effectively
- Feel confident navigating the framework for your own projects

**Time to First Success**: 5-10 minutes
**Difficulty**: Beginner-friendly

---

## What is Lattice Lock?

Lattice Lock is a schema-first framework that orchestrates validation, code generation, and AI-enhanced development. Think of it as having a team of expert tools working together to ensure your code meets your specifications.

### Key Concepts

**Schema (`lattice.yaml`)**: The single source of truth for your project
- Defines entities, relationships, and constraints
- Drives code generation and validation
- Provides consistent structure across your codebase

**Commands**: Specialized CLI tools for different tasks
- **`lattice init`**: Initialize a new project
- **`lattice validate`**: Check schema and project structure
- **`lattice compile`**: Generate Pydantic models and test contracts
- **`lattice test`**: Run contract tests against your code
- **`lattice sheriff`**: Enforce code quality rules

**Model Orchestrator**: Intelligent system that selects optimal AI models for AI-powered commands
- Balances quality, cost, and speed
- Supports multiple providers (local and cloud)
- Automatic fallback when models are unavailable

### Why Use Lattice Lock?

**Traditional Approach**:
- Manually maintain models and validation
- Hope code matches documentation
- Risk inconsistent implementations
- No automated contract testing

**Lattice Lock Approach**:
- Schema-first development with auto-generation
- Consistent code from validated schemas
- Automatic contract test generation
- AI-enhanced development with cost optimization

---

## Prerequisites

Before starting, ensure you have:

### Required

- **Lattice Lock CLI** installed
- **Git** for version control
- **Python 3.8+** for the framework
- **Text editor** for viewing files

### Optional (Recommended)

- **Ollama** for local models (free, privacy-preserving)
- **Cloud API Keys** for premium models (Anthropic, OpenAI, Google)

### Quick Environment Check

```bash
# Verify Python
python3 --version  # Should be 3.8+

# Verify Git
git --version

# Verify Lattice Lock
lattice --version

# Check if Ollama installed (optional)
which ollama || echo "Ollama not installed (optional)"
```

**Don't worry if you don't have everything yet!** You can complete the first tutorial with just Python and the Lattice Lock CLI.

---

## Your First Success: 10-Minute Quick Win

Let's get you a successful result in the next 10 minutes.

### Step 1: Navigate to Your Project Directory (30 seconds)

```bash
# Navigate to your project (replace with your actual path)
cd /path/to/your/project
pwd  # Verify you're in the right place
```

### Step 2: Initialize Lattice Lock (1 minute)

```bash
# Initialize a new Lattice Lock project
lattice init my_project --type service

# Or if you already have a project
lattice doctor
```

**Expected Output**: Project structure created or environment validated.

### Step 3: Review Project Structure (30 seconds)

```bash
# Check key files exist
ls lattice.yaml        # Schema definition
ls -d src/ tests/      # Generated directories
```

**What to Notice**:
- `lattice.yaml`: Your schema definition file
- `src/`: Application source code
- `tests/`: Generated test contracts

### Step 4: Understanding the Schema (2 minutes)

Open `lattice.yaml` to see the schema structure:

```yaml
# Example lattice.yaml
name: my_project
version: 1.0.0

entities:
  User:
    fields:
      id: uuid
      name: string
      email: email
    constraints:
      - unique: email
```

**Key Elements**:
- **entities**: Define your data models
- **fields**: Specify types and constraints
- **constraints**: Validation rules

### Step 5: Your First Validation (2 minutes)

```bash
# Validate your schema
lattice validate

# See verbose output
lattice validate --verbose
```

**What Happens**:
1. Lattice Lock reads your schema
2. Validates syntax and structure
3. Checks constraint consistency
4. Reports any issues found

**Expected Output**: Schema validation passed or specific errors to fix.

### Step 6: Generate Code (2 minutes)

```bash
# Generate Pydantic models from schema
lattice compile --pydantic

# Check generated files
ls src/models/
```

**What Gets Generated**:
- Pydantic models with type hints
- Validation logic from constraints
- Test contracts for verification

### Step 7: Run Tests (1 minute)

```bash
# Generate and run contract tests
lattice test --generate
lattice test --run
```

**Expected Output**: All contract tests pass, confirming your code matches the schema.

### Checkpoint: First Success Achieved

**Congratulations!** You've just:
- Initialized a Lattice Lock project
- Validated your schema
- Generated code from your schema
- Run contract tests

**Time Elapsed**: 5-10 minutes
**Next Step**: Continue to progressive learning path below

---

## Progressive Learning Path

Now that you have your first success, here's the recommended learning sequence:

### Beginner Level (You Are Here)

**Goal**: Understand schema basics and use core commands

**Next Steps**:
1. Complete [Basic Model Selection Tutorial](./basic_model_selection.md) (10-15 min)
2. Review the [Quick Start Guide](../guides/quick_start.md)
3. Try validating and compiling a more complex schema

**Resources**:
- [Getting Started Guide](../guides/getting_started.md)
- [Configuration Reference](../reference/configuration.md)
- [CLI Overview](../reference/cli/overview.md)

### Intermediate Level

**Goal**: Use advanced validation and code generation features

**Tasks**:
1. Add custom validation rules
2. Set up local AI models with Ollama (optional)
3. Integrate with your IDE

**Resources**:
- [Adding Validation Guide](../advanced/adding_validation.md)
- [Local Models Guide](../guides/local_models.md)
- [IDE Integration Guide](../guides/ide_integration.md)

### Advanced Level

**Goal**: Create custom rules and optimize workflows

**Tasks**:
1. Create custom Sheriff rules
2. Set up multi-project configurations
3. Configure provider strategies

**Resources**:
- [Custom Rules Guide](../advanced/custom_rules.md)
- [Multi-Project Guide](../concepts/multi_project.md)
- [Provider Strategy Guide](../advanced/provider_strategy.md)

### Expert Level

**Goal**: Production deployment and CI/CD integration

**Tasks**:
1. Set up CI/CD integration
2. Configure production deployment
3. Monitor and optimize workflows

**Resources**:
- [CI Integration Guide](../guides/ci_integration.md)
- [Production Deployment Guide](../guides/production_deployment.md)
- [Troubleshooting Guide](../troubleshooting/README.md)

---

## Hands-On Exercises

Practice makes perfect. Try these exercises to solidify your understanding.

### Exercise 1: Command Identification

For each task, identify which command to use:

1. "Check if my schema is valid"
2. "Generate Pydantic models from my schema"
3. "Verify my environment is set up correctly"
4. "Run contract tests against my code"

<details>
<summary>Click to see answers</summary>

1. `lattice validate` (validates schema structure)
2. `lattice compile --pydantic` (generates models)
3. `lattice doctor` (checks environment)
4. `lattice test --run` (runs tests)

</details>

### Exercise 2: Schema Definition

Create a schema for a blog with posts and authors:

```yaml
entities:
  Author:
    fields:
      id: uuid
      name: string
      email: email

  Post:
    fields:
      id: uuid
      title: string
      content: text
      author_id: uuid
    relationships:
      author: Author
```

Then validate it with `lattice validate`.

### Exercise 3: Code Generation

Generate code and explore the output:

```bash
# Generate all artifacts
lattice compile --pydantic --sqlmodel

# Explore generated files
ls src/models/
cat src/models/author.py
```

---

## Validation Checkpoints

Confirm your understanding with these quick checks:

### Checkpoint 1: System Understanding

- [ ] I can explain what Lattice Lock does in one sentence
- [ ] I understand the role of `lattice.yaml`
- [ ] I know the main CLI commands (init, validate, compile, test, sheriff)
- [ ] I understand the schema-to-code generation flow

### Checkpoint 2: First Success

- [ ] I successfully initialized a project
- [ ] I validated a schema without errors
- [ ] I generated Pydantic models
- [ ] I ran contract tests

### Checkpoint 3: Ready for Tutorials

- [ ] I have Python 3.8+ installed
- [ ] I have Lattice Lock CLI installed
- [ ] I know where to find documentation
- [ ] I'm ready to learn advanced features

**All Checked?** Great! You're ready to continue to the next tutorial.

---

## Common Questions at This Stage

### "Do I need API keys for AI features?"

No. Lattice Lock's core features (validation, compilation, testing) work without AI. AI features like `lattice ask` require API keys but are optional.

### "Which commands should I use most often?"

The core workflow is: `validate` -> `compile` -> `test` -> `sheriff`. Use these iteratively during development.

### "What if validation fails?"

Run `lattice validate --verbose` for detailed error messages. Use `lattice validate --fix` for auto-fixable issues.

### "Can I customize the generated code?"

Yes! Use custom rules with Sheriff, or modify the compilation templates. See the [Custom Rules Guide](../advanced/custom_rules.md).

### "How do I integrate with CI/CD?"

See the [CI Integration Guide](../guides/ci_integration.md) for GitHub Actions, GitLab CI, and other platforms.

---

## What's Next?

You've completed the onboarding! Here are your next steps:

### Immediate Next Steps (Choose One)

1. **Learn Model Selection**: [Basic Model Selection Tutorial](./basic_model_selection.md)
2. **Deep Dive**: Read the [Getting Started Guide](../guides/getting_started.md)
3. **Quick Reference**: Bookmark the [CLI Overview](../reference/cli/overview.md)

### This Week

1. Complete the model selection tutorial
2. Set up local models (optional but recommended)
3. Try validating your own project schemas

### This Month

1. Integrate Lattice Lock into your development workflow
2. Set up CI/CD integration
3. Explore advanced features like custom rules

---

## Getting Help

### Documentation Resources

- **Quick Start**: [Quick Start Guide](../guides/quick_start.md)
- **Common Issues**: [Troubleshooting Guide](../troubleshooting/README.md)
- **Error Codes**: [Validation Errors Reference](../troubleshooting/validation_errors.md)
- **CLI Reference**: [CLI Documentation](../reference/cli/README.md)

### Support Channels

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions and share ideas

---

**Onboarding Guide Version**: 2.0
**Last Updated**: 2026-01-31
**Estimated Completion Time**: 10 minutes
**Next Step**: [Basic Model Selection Tutorial](./basic_model_selection.md)

---

**You're ready to go!** Start with the next tutorial when you're ready to learn model selection.
