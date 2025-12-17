import re

from .schema import ValidationResult


def validate_env_file(
    file_path: str, required_vars: list[str] | None = None
) -> ValidationResult:
    """
    Validates an environment variable file (.env).

    Args:
        file_path: Path to the .env file.
        required_vars: List of required environment variable names.

    Returns:
        ValidationResult: The result of the validation.
    """
    if required_vars is None:
        required_vars = ["ORCHESTRATOR_STRATEGY", "LOG_LEVEL"]

    result = ValidationResult()

    try:
        with open(file_path) as f:
            lines = f.readlines()
    except FileNotFoundError:
        result.add_error(f"File not found: {file_path}")
        return result

    found_vars = set()

    # Secret patterns
    secret_key_patterns = [
        r".*_API_KEY$",
        r".*_SECRET$",
        r".*_TOKEN$",
        r".*_PASSWORD$",
        r".*_PASS$",
        r".*_CREDENTIAL$",
        r".*_AUTH$",
    ]

    # Acceptable placeholder patterns
    placeholder_patterns = [
        r"^your-.*-here$",
        r"^<placeholder>$",
        r"^xxx$",
        r"^changeme$",
        r"^$",
        r"^vault:.*$",
        r"^aws-secrets:.*$",
    ]

    for i, line in enumerate(lines):
        line_num = i + 1
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        # Parse KEY=VALUE
        match = re.match(r"^([^=]+)=(.*)$", line)
        if not match:
            # warn about malformed lines?
            continue

        key, value = match.groups()
        key = key.strip()
        value = value.strip()

        # Remove quotes if present
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]

        found_vars.add(key)

        # 1. Validate naming convention (UPPER_SNAKE_CASE)
        if not re.match(r"^[A-Z][A-Z0-9_]*$", key):
            result.add_warning(
                f"Variable '{key}' does not follow UPPER_SNAKE_CASE convention",
                line_number=line_num,
            )

        # 2. Detect secrets
        is_secret_key = any(re.match(p, key) for p in secret_key_patterns)
        if is_secret_key:
            is_placeholder = any(re.match(p, value) for p in placeholder_patterns)
            if not is_placeholder:
                # It looks like a secret key, and the value doesn't look like a placeholder.
                # It might be a real secret.
                result.add_error(
                    f"Potential plaintext secret detected in '{key}'", line_number=line_num
                )

    # 3. Check required variables
    for req_var in required_vars:
        if req_var not in found_vars:
            result.add_error(f"Missing required environment variable: {req_var}")

    return result
