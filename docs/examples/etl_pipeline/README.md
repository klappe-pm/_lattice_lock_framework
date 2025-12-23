# Data Pipeline Pilot Project

A data processing pipeline demonstrating Lattice Lock governance for ETL
(Extract, Transform, Load) operations with validation.

## Overview

This pilot project implements a complete data pipeline with:

- Data extraction from multiple source types (databases, APIs, files)
- Configurable transformation rules (mapping, filtering, aggregation)
- Data loading to various targets (databases, data warehouses, files)
- Validation rules with configurable severity levels

All entities are defined in `lattice.yaml` and validated by the Lattice Lock Framework.

## Project Structure

```
data_pipeline/
├── lattice.yaml           # Schema definition
├── src/
│   ├── extractors/        # Data extraction components
│   ├── transformers/      # Data transformation rules
│   ├── loaders/           # Data loading components
│   └── validators/        # Data validation rules
├── tests/
│   ├── test_extractors.py # Extractor tests
│   ├── test_transformers.py # Transformer tests
│   └── test_validators.py # Validator tests
└── .github/workflows/
    └── ci.yaml            # CI/CD pipeline
```

## Entities

### DataSource
Configuration for data extraction sources (database, API, file, stream).

### DataRecord
Individual data records extracted from sources with status tracking.

### TransformationRule
Rules defining how to transform data (map, filter, aggregate, join, custom).

### TransformedRecord
Data records after transformation with validation status.

### LoadTarget
Configuration for data load destinations (database, data warehouse, file, API).

### LoadJob
Records of data load operations with success/failure counts.

### ValidationRule
Rules for validating transformed data (required, type check, range, regex, custom).

### PipelineRun
Complete pipeline execution records with metrics.

## Schema Constraints

The `lattice.yaml` schema enforces:

- **Field types**: Strict typing for all fields
- **Constraints**: Primary keys, foreign keys, enums, min/max values
- **Ensures**: Business rule validation (e.g., counts must be non-negative)
- **Indexes**: Database indexes for query optimization

## Running Tests

```bash
cd docs/examples/etl_pipeline
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

## Pipeline Components

### Extractors
- `DatabaseExtractor`: Extracts data from SQL databases
- `APIExtractor`: Extracts data from REST APIs
- `FileExtractor`: Extracts data from files (CSV, JSON, etc.)

### Transformers
- `MapTransformer`: Maps fields with transformations (uppercase, prefix, etc.)
- `FilterTransformer`: Filters records based on conditions
- `AggregateTransformer`: Aggregates data (sum, avg, count, min, max)

### Loaders
- `DatabaseLoader`: Loads data to SQL databases
- `DataWarehouseLoader`: Loads data to data warehouses
- `FileLoader`: Loads data to files

### Validators
- `RequiredValidator`: Checks for required fields
- `TypeCheckValidator`: Validates field types
- `RangeValidator`: Validates numeric ranges
- `RegexValidator`: Validates string patterns
