---
title: custom_rules
type: guide
status: stable
categories: [advanced, governance]
sub_categories: [custom_rules]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [adv-custom-rules-001]
tags: [advanced, custom_rules, sheriff, gauntlet]
---

# Custom Rules Guide

Lattice Lock allows you to extend its capabilities by defining custom Sheriff rules for static analysis and custom Gauntlet test generators.

## Custom Sheriff Rules

Sheriff rules enforce structural and stylistic constraints on your codebase.

### Creating a Rule

To create a custom rule, subclass `SheriffRule` and implement the `visit` method. Lattice Lock uses Python's `ast` module for analysis.

```python
# src/rules/no_print.py
import ast
from lattice_lock.sheriff import SheriffRule, Violation

class NoPrintRule(SheriffRule):
    name = "no-print"
    description = "Avoid using print() in production code."

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self.add_violation(
                Violation(
                    message="Found print() statement",
                    line=node.lineno,
                    severity="warning"
                )
            )
```

### Configuration

Register your custom rule in `lattice.yaml`.

```yaml
sheriff:
  custom_rules:
    - src.rules.no_print.NoPrintRule
```

## Custom Gauntlet Test Generators

Gauntlet generates semantic tests based on your schema. You can create custom generators for specific testing needs.

### Generator Structure

A generator takes a model definition and produces test code.

```python
# src/generators/boundary_tester.py
from lattice_lock.gauntlet import TestGenerator, Model

class BoundaryTestGenerator(TestGenerator):
    def generate(self, model: Model) -> str:
        tests = []
        for field in model.fields:
            if field.type == "Integer":
                tests.append(self._create_boundary_test(model.name, field.name))
        return "\n".join(tests)

    def _create_boundary_test(self, model_name, field_name):
        return f"""
def test_{model_name}_{field_name}_boundary():
    # Test logic here
    pass
"""
```

### Registering Generators

Add your generator to the Gauntlet configuration.

```yaml
gauntlet:
  generators:
    - src.generators.boundary_tester.BoundaryTestGenerator
```

## Sharing Rules

To share rules across projects:

1. **Package your rules**: Create a Python package containing your rule definitions.
2. **Install the package**: Install it in your target projects via pip.
3. **Reference in config**: Use the full import path in `lattice.yaml`.

```yaml
sheriff:
  custom_rules:
    - my_company_rules.security.NoHardcodedSecrets
```
