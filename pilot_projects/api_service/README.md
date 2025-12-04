# API Service Pilot Project

A REST API service demonstrating Lattice Lock governance for schema validation,
constraint enforcement, and deterministic code generation.

## Overview

This pilot project implements a complete e-commerce API with:

- User authentication and management
- Product catalog with inventory tracking
- Order management with status workflow
- Payment processing with transaction tracking

All entities are defined in `lattice.yaml` and validated by the Lattice Lock Framework.

## Project Structure

```
api_service/
├── lattice.yaml           # Schema definition
├── src/
│   ├── api/               # REST API endpoints
│   ├── models/            # Data models (generated from schema)
│   └── services/          # Business logic
├── tests/
│   ├── test_models.py     # Model constraint tests
│   └── test_services.py   # Service logic tests
└── .github/workflows/
    └── ci.yaml            # CI/CD pipeline
```

## Entities

### User
User accounts with authentication credentials and verification status.

### Product
Product catalog items with SKU, pricing, and inventory tracking.

### Order
Customer orders with status workflow (pending → confirmed → processing → shipped → delivered).

### OrderItem
Line items linking orders to products with quantity and pricing.

### Payment
Payment transactions with multiple payment methods and currencies.

## Schema Constraints

The `lattice.yaml` schema enforces:

- **Field types**: Strict typing for all fields
- **Constraints**: Primary keys, foreign keys, unique constraints, min/max values
- **Ensures**: Business rule validation (e.g., prices must be non-negative)
- **Indexes**: Database indexes for query optimization

## Running Tests

```bash
cd pilot_projects/api_service
PYTHONPATH=. pytest tests/ -v
```

## CI/CD Pipeline

The GitHub Actions workflow includes:

1. **Lint**: Ruff linter and formatter, MyPy type checking
2. **Test**: pytest with coverage reporting
3. **Lattice Validate**: Schema validation and constraint checking
4. **Security Scan**: Bandit security analysis

## Lattice Lock Integration

This project demonstrates:

1. **Schema-first development**: All entities defined in `lattice.yaml`
2. **Constraint enforcement**: Models validate constraints at runtime
3. **Deterministic generation**: Code generated from schema is reproducible
4. **Governance compliance**: CI validates schema before deployment
