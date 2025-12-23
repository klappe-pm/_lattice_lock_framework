import re
from typing import Any

import yaml

from .schema import ValidationResult


def validate_agent_manifest(file_path: str) -> ValidationResult:
    """
    Validates an agent manifest file.

    Args:
        file_path: Path to the agent manifest file (YAML).

    Returns:
        ValidationResult: The result of the validation.
    """
    result = ValidationResult()

    try:
        with open(file_path) as f:
            content = f.read()
            data = yaml.safe_load(content)
    except FileNotFoundError:
        result.add_error(f"File not found: {file_path}")
        return result
    except yaml.YAMLError as e:
        line = e.problem_mark.line + 1 if hasattr(e, "problem_mark") else None
        result.add_error(f"Invalid YAML format: {str(e)}", line_number=line)
        return result

    if not isinstance(data, dict):
        result.add_error("Root element must be a dictionary")
        return result

    # 1. Validate top-level sections
    # Spec says: agent.identity, directive, responsibilities, scope
    # Note: 'agent.identity' in prompt implies nested structure or a key named 'agent.identity'?
    # Looking at standard YAMLs, it's usually:
    # agent:
    #   identity: ...
    # But prompt says "Check required sections: agent.identity, directive, responsibilities, scope"
    # and "Validate agent.identity fields: name, version..."

    has_inheritance = False
    if "agent" not in data:
        result.add_error("Missing required top-level section: agent")
    else:
        agent_section = data["agent"]
        if not isinstance(agent_section, dict):
            result.add_error("'agent' section must be a dictionary")
        elif "identity" not in agent_section:
            result.add_error("Missing required section: agent.identity")
        else:
            _validate_identity(agent_section["identity"], result)
            if isinstance(agent_section["identity"], dict) and "inherits_from" in agent_section["identity"]:
                has_inheritance = True

    # Directive, Responsibilities, and Scope are required UNLESS inheriting
    if "directive" not in data:
        if not has_inheritance:
            result.add_error("Missing required top-level section: directive")
    else:
        _validate_directive(data["directive"], result)

    if "responsibilities" not in data:
        if not has_inheritance:
            result.add_error("Missing required top-level section: responsibilities")
    else:
        _validate_responsibilities(data["responsibilities"], result)

    if "scope" not in data:
        if not has_inheritance:
            result.add_error("Missing required top-level section: scope")
    else:
        _validate_scope(data["scope"], result)

    return result


def _validate_identity(identity: Any, result: ValidationResult):
    """Validates the agent identity section."""
    if not isinstance(identity, dict):
        result.add_error("agent.identity must be a dictionary")
        return

    required_fields = ["name", "version", "description", "role"]
    for field in required_fields:
        if field not in identity:
            result.add_error(f"Missing required field in agent.identity: {field}")
        elif not isinstance(identity[field], str) or not identity[field].strip():
            result.add_error(f"Field 'agent.identity.{field}' must be a non-empty string")

    if "version" in identity and isinstance(identity["version"], str):
        version = identity["version"]
        if not re.match(r"^v?\d+\.\d+(?:\.\d+)?$", version):
            result.add_error(
                f"Invalid version format: {version}. Must be semantic version (e.g., 1.0.0 or v1.0.0)"
            )


def _validate_directive(directive: Any, result: ValidationResult):
    """Validates the agent directive section."""
    if not isinstance(directive, dict):
        result.add_error("directive section must be a dictionary")
        return

    if "primary_goal" not in directive:
        result.add_error("Missing required field in directive: primary_goal")
    elif not isinstance(directive["primary_goal"], str) or not directive["primary_goal"].strip():
        result.add_error("Field 'directive.primary_goal' must be a non-empty string")

    if "constraints" in directive:
        if not isinstance(directive["constraints"], list):
            result.add_error("Field 'directive.constraints' must be a list")


def _validate_responsibilities(responsibilities: Any, result: ValidationResult):
    """Validates the agent responsibilities section."""
    if not isinstance(responsibilities, list):
        result.add_error("responsibilities section must be a list")
        return

    for i, resp in enumerate(responsibilities):
        if not isinstance(resp, dict):
            result.add_error(f"Responsibility item #{i+1} must be a dictionary")
            continue

        if "name" not in resp:
            result.add_error(f"Responsibility item #{i+1} missing required field: name")
        if "description" not in resp:
            result.add_error(f"Responsibility item #{i+1} missing required field: description")


def _validate_scope(scope: Any, result: ValidationResult):
    """Validates the agent scope section."""
    if not isinstance(scope, dict):
        result.add_error("scope section must be a dictionary")
        return

    # Prompt implies checking scope exists, but doesn't explicitly list required fields inside scope
    # other than mentioning "can_access, cannot_access" in step 2.
    # Let's check for them if they are required. Step 2 says: "scope (can_access, cannot_access)".
    # I'll treat them as required based on that.

    if "can_access" not in scope:
        result.add_error("Missing required field in scope: can_access")
    
    # cannot_access is optional in some versions but recommended
    if "cannot_access" in scope:
        if not isinstance(scope["cannot_access"], list):
            result.add_error("Field 'scope.cannot_access' must be a list")
