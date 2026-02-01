---
title: advanced_validation
type: guide
status: stable
categories: [advanced, validation]
sub_categories: [constraints]
date_created: 2024-12-10
date_revised: 2026-01-31
file_ids: [adv-validation-001]
tags: [advanced, validation, constraints, cross_entity]
---

# Advanced Validation Guide

This guide covers complex validation scenarios in Lattice Lock, including cross-entity constraints, custom logic, and performance optimization.

## Complex Constraint Patterns

Lattice Lock supports advanced constraint patterns beyond simple type checking.

### Conditional Validation

You can apply constraints based on the value of other fields using the `when` clause.

```yaml
models:
  Transaction:
    fields:
      type: String
      amount: Float
      currency: String
    constraints:
      - check: amount > 0
      - check: amount < 10000
        when: type == "standard"
      - check: currency == "USD"
        when: amount > 1000000
```

### Regular Expressions

Use regex for precise string format validation.

```yaml
models:
  User:
    fields:
      username: String
    constraints:
      - check: regex(username, "^[a-z0-9_-]{3,16}$")
```

## Cross-Entity Validation

Validating relationships between different entities ensures data integrity across your domain model.

### Reference Checking

Ensure that a referenced entity exists and satisfies specific conditions.

```yaml
models:
  Order:
    fields:
      customerId: String
      total: Float
    constraints:
      - check: exists(Customer, id=customerId)
      - check: lookup(Customer, id=customerId).status == "active"
```

*Note: Cross-entity validation may require database access. Ensure your validator is configured with a data loader.*

## Custom Ensures Clauses

For validation logic that cannot be expressed in standard Lattice Lock syntax, you can implement custom ensures clauses in Python.

1. **Define the Custom Check**

   Create a Python function decorated with `@lattice.validator`.

   ```python
   # src/validators/custom.py
   from lattice_lock import validator

   @validator("is_valid_luhn")
   def validate_luhn(value: str) -> bool:
       # Implementation of Luhn algorithm
       return True
   ```

2. **Register the Validator**

   Ensure your custom validator module is imported in your application entry point.

3. **Use in Schema**

   ```yaml
   models:
     CreditCard:
       fields:
         number: String
       constraints:
         - check: is_valid_luhn(number)
   ```

## Validation Performance Optimization

Validation can become a bottleneck if not managed correctly, especially with complex cross-entity checks.

### Caching Strategy

Enable caching for reference lookups to reduce database hits.

```python
from lattice_lock.config import ValidationConfig

config = ValidationConfig(
    cache_enabled=True,
    cache_ttl=60  # seconds
)
```

### Selective Validation

Validate only changed fields during updates instead of the entire object graph.

```python
validator.validate(order, fields=["status", "updatedAt"])
```

### Batch Validation

When processing large datasets, use batch validation to minimize overhead.

```python
results = validator.validate_batch(orders)
```
