import re
import yaml
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class ValidationError:
    message: str
    line_number: Optional[int] = None
    field_path: Optional[str] = None

@dataclass
class ValidationWarning:
    message: str
    line_number: Optional[int] = None
    field_path: Optional[str] = None

@dataclass
class ValidationResult:
    valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationWarning] = field(default_factory=list)

    def add_error(self, message: str, line_number: Optional[int] = None, field_path: Optional[str] = None):
        self.valid = False
        self.errors.append(ValidationError(message, line_number, field_path))

    def add_warning(self, message: str, line_number: Optional[int] = None, field_path: Optional[str] = None):
        self.warnings.append(ValidationWarning(message, line_number, field_path))

def validate_lattice_schema(file_path: str) -> ValidationResult:
    result = ValidationResult()
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Use safe_load to avoid arbitrary code execution
            data = yaml.safe_load(content)
    except FileNotFoundError:
        result.add_error(f"File not found: {file_path}")
        return result
    except yaml.YAMLError as e:
        line = e.problem_mark.line + 1 if hasattr(e, 'problem_mark') else None
        result.add_error(f"Invalid YAML format: {str(e)}", line_number=line)
        return result

    if not isinstance(data, dict):
        result.add_error("Root element must be a dictionary")
        return result

    # 1. Check required sections
    required_sections = ['version', 'generated_module', 'entities']
    for section in required_sections:
        if section not in data:
            result.add_error(f"Missing required section: {section}")
    
    if not result.valid and not data.get('entities'): # Stop if critical sections missing, but continue if only some missing to find more errors
         pass 

    # 2. Validate version format
    if 'version' in data:
        version = str(data['version'])
        if not re.match(r'^v\d+\.\d+(?:\.\d+)?$', version):
            result.add_error(f"Invalid version format: {version}. Must be vX.Y or vX.Y.Z", field_path="version")

    # 3. Validate entities
    defined_entities = set()
    if 'entities' in data and isinstance(data['entities'], dict):
        for entity_name, entity_def in data['entities'].items():
            defined_entities.add(entity_name)
            _validate_entity(entity_name, entity_def, result)
    elif 'entities' in data:
        result.add_error("Entities section must be a dictionary", field_path="entities")

    # 4. Validate interfaces (if present) to check entity references
    if 'interfaces' in data and isinstance(data['interfaces'], dict):
        for interface_name, interface_def in data['interfaces'].items():
            _validate_interface(interface_name, interface_def, defined_entities, result)

    return result

def _validate_entity(entity_name: str, entity_def: Any, result: ValidationResult):
    if not isinstance(entity_def, dict):
        result.add_error(f"Definition for entity '{entity_name}' must be a dictionary", field_path=f"entities.{entity_name}")
        return

    if 'fields' not in entity_def:
        result.add_error(f"Entity '{entity_name}' missing 'fields' section", field_path=f"entities.{entity_name}")
        return

    if not isinstance(entity_def['fields'], dict):
        result.add_error(f"Fields for entity '{entity_name}' must be a dictionary", field_path=f"entities.{entity_name}.fields")
        return

    for field_name, field_def in entity_def['fields'].items():
        _validate_field(entity_name, field_name, field_def, result)

def _validate_field(entity_name: str, field_name: str, field_def: Any, result: ValidationResult):
    path = f"entities.{entity_name}.fields.{field_name}"
    
    if not isinstance(field_def, dict):
        result.add_error(f"Definition for field '{field_name}' must be a dictionary", field_path=path)
        return

    # Validate type
    valid_types = {'uuid', 'str', 'int', 'decimal', 'bool', 'enum'}
    field_type = field_def.get('type')
    
    # Enum is a special case where type might be implicit if enum values are provided, 
    # but spec says "type: enum". Let's stick to spec: "type: enum" or one of the others.
    # Actually spec example: "status: { enum: [pending, filled, cancelled], default: pending }" 
    # implies 'type' key might be missing if 'enum' key is present? 
    # The prompt says: "Validate field types (supported: uuid, str, int, decimal, bool, enum)"
    # I will assume 'type' is required unless 'enum' is present, or 'type: enum' is explicitly used.
    
    if 'enum' in field_def:
        if 'type' in field_def and field_def['type'] != 'enum':
             result.add_error(f"Field '{field_name}' has enum values but type is '{field_def['type']}'", field_path=path)
        if not isinstance(field_def['enum'], list):
             result.add_error(f"Enum values for field '{field_name}' must be a list", field_path=path)
    elif 'type' in field_def:
        if field_def['type'] not in valid_types:
            result.add_error(f"Unsupported field type: '{field_def['type']}'", field_path=path)
    else:
        result.add_error(f"Field '{field_name}' missing type definition", field_path=path)

    # Validate constraints
    valid_constraints = {'gt', 'lt', 'gte', 'lte', 'unique', 'primary_key', 'default', 'scale', 'nullable'} 
    # Added 'default', 'scale', 'nullable' as they appear in spec examples or are common. 
    # Prompt specifically lists: gt, lt, gte, lte, unique, primary_key.
    
    for key in field_def:
        if key not in valid_constraints and key != 'type' and key != 'enum':
            # We could warn about unknown keys, but let's stick to validating known constraints
            pass
            
    # Check numeric constraints on non-numeric types?
    numeric_constraints = {'gt', 'lt', 'gte', 'lte'}
    if any(k in field_def for k in numeric_constraints):
        if field_type not in ('int', 'decimal') and 'enum' not in field_def: 
             # Enums usually aren't numeric in this context, but could be. 
             # For now, let's just check if type is explicitly non-numeric
             if field_type in ('uuid', 'str', 'bool'):
                 result.add_error(f"Numeric constraints used on non-numeric field '{field_name}'", field_path=path)

def _validate_interface(interface_name: str, interface_def: Any, defined_entities: set, result: ValidationResult):
    if not isinstance(interface_def, dict):
        return # Basic structural error would be caught elsewhere or ignored here

    if 'methods' in interface_def and isinstance(interface_def['methods'], dict):
        for method_name, method_def in interface_def['methods'].items():
            if 'params' in method_def and isinstance(method_def['params'], dict):
                for param_name, param_type in method_def['params'].items():
                    # param_type could be a simple string referring to an Entity
                    if isinstance(param_type, str):
                        if param_type in defined_entities:
                            continue
                        # It might be a basic type, but the prompt says "Validate entity references (entities must be defined before referenced)"
                        # Usually basic types are lower case, entities are CamelCase.
                        # Let's assume if it looks like an entity (starts with uppercase), it must be defined.
                        if param_type[0].isupper() and param_type not in defined_entities:
                             result.add_error(f"Undefined entity reference '{param_type}' in method '{method_name}'", field_path=f"interfaces.{interface_name}.methods.{method_name}.params.{param_name}")

