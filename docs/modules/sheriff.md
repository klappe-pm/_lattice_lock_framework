# Sheriff Governance

**Sheriff** is the policy enforcement engine of Lattice Lock. Is validates your project structure, code quality, and compliance with governance rules defined in `lattice.yaml`.

## Key Features

- **Rule Enforcement**: Checks file existence, regex patterns, and unauthorized dependencies.
- **Validation**: Ensures `lattice.yaml` itself is valid.
- **Reporting**: Outputs detailed success/failure reports in text or JSON.
- **MCP Tool**: Available as `validate_code` in the MCP server.

## Usage

```bash
# Validate current directory
lattice validate

# Validate specific path
lattice validate --path /path/to/project

# JSON Output
lattice validate --json
```

## Configuration

Rules are defined in `lattice.yaml` under the `sheriff` section.
