"""
Lattice Lock Compiler - Normalization and Denormalization

This module provides strategies for normalizing hierarchical configurations
into flat, tabular structures optimized for TOON format, and denormalizing
back to hierarchical structures for JSON/YAML output.

Normalization Strategy:
    Hierarchical (nested objects/arrays) → Relational (flat tables with IDs)
    
Denormalization Strategy:
    Relational (flat tables) → Hierarchical (nested objects/arrays)

This is critical for:
    1. Token efficiency in TOON format (uniform arrays)
    2. Cross-referencing at scale (agents, schemas, models)
    3. JSON interoperability (hedge format)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import uuid


class NormalizationStrategy(str, Enum):
    """Normalization strategies for different config types."""
    
    NONE = "none"           # No normalization
    FLATTEN = "flatten"     # Flatten nested objects
    RELATIONAL = "relational"  # Full relational normalization with IDs
    AUTO = "auto"           # Auto-detect best strategy


@dataclass
class NormalizationConfig:
    """
    Configuration for normalization behavior.
    
    Attributes:
        strategy: Normalization strategy
        generate_ids: Generate IDs for records
        id_prefix: Prefix for generated IDs
        flatten_depth: Maximum depth to flatten (-1 for unlimited)
        preserve_keys: Keys to preserve unnormalized
        table_threshold: Minimum array size to normalize
    """
    
    strategy: NormalizationStrategy = NormalizationStrategy.AUTO
    generate_ids: bool = True
    id_prefix: str = ""
    flatten_depth: int = -1
    preserve_keys: list[str] = field(default_factory=lambda: ["_meta"])
    table_threshold: int = 2


class Normalizer:
    """
    Normalizes hierarchical configurations for TOON efficiency.
    
    The normalizer transforms nested structures into flat, relational tables
    that can be efficiently represented in TOON's tabular format.
    
    Example:
        normalizer = Normalizer()
        
        # Input: nested agent config
        nested = {
            "agents": {
                "engineering": {
                    "subagents": ["backend", "frontend"]
                }
            }
        }
        
        # Output: normalized tables
        normalized = normalizer.normalize(nested)
        # {
        #     "agents": [{"id": "agt_1", "name": "engineering"}],
        #     "agent_subagents": [
        #         {"agent_id": "agt_1", "subagent": "backend"},
        #         {"agent_id": "agt_1", "subagent": "frontend"}
        #     ]
        # }
    """
    
    def __init__(self, config: NormalizationConfig | None = None):
        """
        Initialize normalizer with configuration.
        
        Args:
            config: Normalization configuration
        """
        self.config = config or NormalizationConfig()
        self._id_counter = 0
    
    def normalize(self, data: dict, strategy: NormalizationStrategy | None = None) -> dict:
        """
        Normalize data for TOON format.
        
        Args:
            data: Input data dict
            strategy: Override normalization strategy
            
        Returns:
            Normalized data dict with flat tables
        """
        strategy = strategy or self.config.strategy
        
        if strategy == NormalizationStrategy.NONE:
            return data
        
        if strategy == NormalizationStrategy.AUTO:
            strategy = self._detect_strategy(data)
        
        if strategy == NormalizationStrategy.FLATTEN:
            return self._flatten(data)
        
        if strategy == NormalizationStrategy.RELATIONAL:
            return self._normalize_relational(data)
        
        return data
    
    def denormalize(self, data: dict) -> dict:
        """
        Denormalize relational data back to hierarchical structure.
        
        Args:
            data: Normalized data with flat tables
            
        Returns:
            Hierarchical data dict
        """
        # Check if data has normalization markers
        if "_normalized" not in data and "_tables" not in data:
            return data
        
        return self._denormalize_relational(data)
    
    def _detect_strategy(self, data: dict) -> NormalizationStrategy:
        """Auto-detect best normalization strategy."""
        # Check for known normalizable patterns
        normalizable_keys = {"entities", "agents", "models", "interfaces", "fields"}
        
        for key in normalizable_keys:
            if key in data:
                value = data[key]
                if isinstance(value, dict) and len(value) >= self.config.table_threshold:
                    return NormalizationStrategy.RELATIONAL
                if isinstance(value, list) and len(value) >= self.config.table_threshold:
                    # Check if items are uniform
                    if self._is_uniform_array(value):
                        return NormalizationStrategy.RELATIONAL
        
        return NormalizationStrategy.FLATTEN
    
    def _is_uniform_array(self, arr: list) -> bool:
        """Check if array items have uniform structure."""
        if not arr or len(arr) < 2:
            return True
        
        if not all(isinstance(item, dict) for item in arr):
            return False
        
        first_keys = set(arr[0].keys())
        return all(set(item.keys()) == first_keys for item in arr)
    
    def _generate_id(self, prefix: str = "") -> str:
        """Generate a unique ID."""
        self._id_counter += 1
        prefix = prefix or self.config.id_prefix
        return f"{prefix}{self._id_counter:04d}"
    
    # =========================================================================
    # Flatten Strategy
    # =========================================================================
    
    def _flatten(self, data: dict, depth: int = 0) -> dict:
        """
        Flatten nested objects using dotted key notation.
        
        Example:
            {"a": {"b": {"c": 1}}} → {"a.b.c": 1}
        """
        if self.config.flatten_depth >= 0 and depth >= self.config.flatten_depth:
            return data
        
        result = {}
        
        for key, value in data.items():
            if key in self.config.preserve_keys:
                result[key] = value
                continue
            
            if isinstance(value, dict) and not self._is_leaf_dict(value):
                flattened = self._flatten(value, depth + 1)
                for sub_key, sub_value in flattened.items():
                    result[f"{key}.{sub_key}"] = sub_value
            else:
                result[key] = value
        
        return result
    
    def _is_leaf_dict(self, d: dict) -> bool:
        """Check if dict is a leaf (contains only primitives)."""
        for value in d.values():
            if isinstance(value, (dict, list)):
                return False
        return True
    
    # =========================================================================
    # Relational Normalization
    # =========================================================================
    
    def _normalize_relational(self, data: dict) -> dict:
        """
        Normalize to relational tables with foreign keys.
        
        Transforms:
            - Dict of dicts → Array of records with IDs
            - Nested arrays → Junction tables
            - Nested objects → Separate tables with foreign keys
        """
        result = {
            "_normalized": True,
            "_tables": [],
        }
        
        # Preserve non-normalizable keys
        for key in self.config.preserve_keys:
            if key in data:
                result[key] = data[key]
        
        # Process each top-level key
        for key, value in data.items():
            if key in self.config.preserve_keys:
                continue
            
            if isinstance(value, dict):
                tables = self._normalize_dict_of_dicts(key, value)
                for table_name, table_data in tables.items():
                    result[table_name] = table_data
                    result["_tables"].append(table_name)
            
            elif isinstance(value, list):
                if self._is_uniform_array(value):
                    result[key] = self._normalize_uniform_array(key, value)
                    result["_tables"].append(key)
                else:
                    result[key] = value
            
            else:
                result[key] = value
        
        return result
    
    def _normalize_dict_of_dicts(self, name: str, data: dict) -> dict[str, list]:
        """
        Normalize a dict of dicts into tables.
        
        Example:
            {"entities": {"User": {...}, "Order": {...}}}
            → {"entities": [{"id": "ent_1", "name": "User", ...}]}
        """
        tables = {}
        main_table = []
        child_tables = {}
        
        for item_name, item_data in data.items():
            if not isinstance(item_data, dict):
                continue
            
            record_id = self._generate_id(f"{name[:3]}_")
            record = {
                "_id": record_id,
                "name": item_name,
            }
            
            for field_key, field_value in item_data.items():
                if isinstance(field_value, dict):
                    # Nested dict → flatten or create child table
                    child_table_name = f"{name}_{field_key}"
                    child_records = self._normalize_nested_dict(
                        child_table_name, record_id, name, field_value
                    )
                    if child_table_name not in child_tables:
                        child_tables[child_table_name] = []
                    child_tables[child_table_name].extend(child_records)
                
                elif isinstance(field_value, list):
                    # Array → junction table or inline
                    if self._should_create_junction_table(field_value):
                        junction_name = f"{name}_{field_key}"
                        junction_records = self._normalize_array_to_junction(
                            junction_name, record_id, f"{name}_id", field_value
                        )
                        if junction_name not in child_tables:
                            child_tables[junction_name] = []
                        child_tables[junction_name].extend(junction_records)
                    else:
                        # Keep inline for small/simple arrays
                        record[field_key] = self._serialize_inline_array(field_value)
                
                else:
                    record[field_key] = field_value
            
            main_table.append(record)
        
        tables[name] = main_table
        tables.update(child_tables)
        
        return tables
    
    def _normalize_nested_dict(
        self,
        table_name: str,
        parent_id: str,
        parent_key: str,
        data: dict,
    ) -> list[dict]:
        """Normalize a nested dict into child records."""
        records = []
        
        for field_name, field_value in data.items():
            record = {
                f"{parent_key}_id": parent_id,
                "field_name": field_name,
            }
            
            if isinstance(field_value, dict):
                # Flatten nested dict fields
                for k, v in field_value.items():
                    if not isinstance(v, (dict, list)):
                        record[k] = v
            else:
                record["value"] = field_value
            
            records.append(record)
        
        return records
    
    def _normalize_uniform_array(self, name: str, data: list) -> list[dict]:
        """Normalize a uniform array, adding IDs if needed."""
        result = []
        
        for i, item in enumerate(data):
            if isinstance(item, dict):
                record = {"_id": self._generate_id(f"{name[:3]}_")}
                record.update(item)
                result.append(record)
            else:
                result.append(item)
        
        return result
    
    def _normalize_array_to_junction(
        self,
        table_name: str,
        parent_id: str,
        parent_key: str,
        data: list,
    ) -> list[dict]:
        """Normalize an array into a junction table."""
        records = []
        
        for item in data:
            if isinstance(item, dict):
                record = {parent_key: parent_id}
                record.update(item)
                records.append(record)
            else:
                records.append({
                    parent_key: parent_id,
                    "value": item,
                })
        
        return records
    
    def _should_create_junction_table(self, arr: list) -> bool:
        """Determine if array should become a junction table."""
        if len(arr) < self.config.table_threshold:
            return False
        
        # Create junction for arrays of dicts
        if all(isinstance(item, dict) for item in arr):
            return True
        
        return False
    
    def _serialize_inline_array(self, arr: list) -> str:
        """Serialize small array to inline string."""
        if all(isinstance(item, str) for item in arr):
            return ";".join(arr)
        return str(arr)
    
    # =========================================================================
    # Denormalization
    # =========================================================================
    
    def _denormalize_relational(self, data: dict) -> dict:
        """
        Denormalize relational tables back to hierarchical structure.
        
        Reconstructs nested objects from flat tables using foreign keys.
        """
        result = {}
        tables = data.get("_tables", [])
        
        # Copy preserved keys
        for key in self.config.preserve_keys:
            if key in data and key != "_meta":
                result[key] = data[key]
        
        # Group tables by parent relationship
        main_tables = []
        child_tables = {}
        
        for table_name in tables:
            if "_" in table_name and table_name.split("_")[0] in tables:
                parent = table_name.split("_")[0]
                if parent not in child_tables:
                    child_tables[parent] = []
                child_tables[parent].append(table_name)
            else:
                main_tables.append(table_name)
        
        # Process main tables
        for table_name in main_tables:
            table_data = data.get(table_name, [])
            
            if not table_data:
                continue
            
            # Check if it's a dict-of-dicts pattern (has 'name' field)
            if isinstance(table_data, list) and table_data and "name" in table_data[0]:
                result[table_name] = self._denormalize_dict_of_dicts(
                    table_name, table_data, child_tables.get(table_name, []), data
                )
            else:
                # Keep as array, removing internal IDs
                result[table_name] = [
                    {k: v for k, v in record.items() if not k.startswith("_")}
                    for record in table_data
                ]
        
        return result
    
    def _denormalize_dict_of_dicts(
        self,
        table_name: str,
        records: list,
        child_table_names: list,
        all_data: dict,
    ) -> dict:
        """Denormalize array back to dict-of-dicts."""
        result = {}
        
        for record in records:
            item_name = record.get("name")
            if not item_name:
                continue
            
            item_data = {
                k: v for k, v in record.items()
                if k not in ("_id", "name")
            }
            
            # Restore child data
            record_id = record.get("_id")
            for child_table_name in child_table_names:
                child_data = all_data.get(child_table_name, [])
                related = [
                    r for r in child_data
                    if r.get(f"{table_name}_id") == record_id
                ]
                
                if related:
                    # Determine field name from table name
                    field_name = child_table_name.replace(f"{table_name}_", "")
                    
                    # Check if it should be a dict or array
                    if all("field_name" in r for r in related):
                        # Nested dict pattern
                        item_data[field_name] = {
                            r["field_name"]: self._extract_child_value(r)
                            for r in related
                        }
                    else:
                        # Array pattern
                        item_data[field_name] = [
                            self._extract_child_value(r)
                            for r in related
                        ]
            
            # Parse inline arrays back to lists
            for key, value in list(item_data.items()):
                if isinstance(value, str) and ";" in value:
                    item_data[key] = value.split(";")
            
            result[item_name] = item_data
        
        return result
    
    def _extract_child_value(self, record: dict) -> Any:
        """Extract the value from a child record."""
        # Remove foreign key and internal fields
        clean = {
            k: v for k, v in record.items()
            if not k.endswith("_id") and not k.startswith("_") and k != "field_name"
        }
        
        # If only 'value' field, return it directly
        if list(clean.keys()) == ["value"]:
            return clean["value"]
        
        return clean


# =========================================================================
# Specialized Normalizers for Lattice Lock Config Types
# =========================================================================

class AgentNormalizer(Normalizer):
    """
    Specialized normalizer for agent definition files.
    
    Transforms:
        agents/engineering_agent/definition.yaml
        
    Into normalized tables:
        - agents: Core agent records
        - agent_subagents: Agent-subagent relationships
        - agent_capabilities: Agent capabilities/use cases
        - agent_scopes: Access/modify scopes
    """
    
    def normalize_agents(self, agents_data: dict | list) -> dict:
        """Normalize agent definitions into relational tables."""
        result = {
            "agents": [],
            "agent_subagents": [],
            "agent_capabilities": [],
            "agent_scopes": [],
        }
        
        # Handle both dict and list inputs
        if isinstance(agents_data, dict):
            items = [
                (name, data) for name, data in agents_data.items()
            ]
        else:
            items = [
                (a.get("name", f"agent_{i}"), a)
                for i, a in enumerate(agents_data)
            ]
        
        for name, agent_data in items:
            agent_id = self._generate_id("agt_")
            
            # Extract identity fields
            identity = agent_data.get("identity", agent_data.get("agent", {}).get("identity", {}))
            directive = agent_data.get("directive", agent_data.get("agent", {}).get("directive", {}))
            scope = agent_data.get("scope", agent_data.get("agent", {}).get("scope", {}))
            delegation = agent_data.get("delegation", agent_data.get("agent", {}).get("delegation", {}))
            
            # Main agent record
            agent_record = {
                "_id": agent_id,
                "name": identity.get("name", name),
                "version": identity.get("version", "1.0.0"),
                "description": identity.get("description", ""),
                "role": identity.get("role", ""),
                "status": identity.get("status", "beta"),
                "primary_goal": directive.get("primary_goal", ""),
            }
            result["agents"].append(agent_record)
            
            # Subagents
            for subagent in delegation.get("allowed_subagents", []):
                result["agent_subagents"].append({
                    "agent_id": agent_id,
                    "subagent_name": subagent.get("name", ""),
                    "subagent_file": subagent.get("file", ""),
                })
            
            # Capabilities / use cases
            for use_case in directive.get("primary_use_cases", []):
                result["agent_capabilities"].append({
                    "agent_id": agent_id,
                    "capability_type": "use_case",
                    "capability_value": use_case,
                })
            
            # Scopes
            for access_path in scope.get("can_access", []):
                result["agent_scopes"].append({
                    "agent_id": agent_id,
                    "scope_type": "access",
                    "path": access_path,
                })
            for modify_path in scope.get("can_modify", []):
                result["agent_scopes"].append({
                    "agent_id": agent_id,
                    "scope_type": "modify",
                    "path": modify_path,
                })
        
        return result


class SchemaNormalizer(Normalizer):
    """
    Specialized normalizer for lattice.yaml schema files.
    
    Transforms entity definitions into:
        - schemas: Core entity records
        - fields: Field definitions
        - field_constraints: Field constraints (gte, lte, etc.)
        - ensures: Ensure clauses
        - indexes: Index definitions
    """
    
    def normalize_schema(self, schema_data: dict) -> dict:
        """Normalize lattice.yaml schema into relational tables."""
        result = {
            "schemas": [],
            "fields": [],
            "field_constraints": [],
            "ensures": [],
            "indexes": [],
        }
        
        entities = schema_data.get("entities", {})
        
        for entity_name, entity_data in entities.items():
            schema_id = self._generate_id("sch_")
            
            # Schema record
            result["schemas"].append({
                "_id": schema_id,
                "name": entity_name,
                "description": entity_data.get("description", ""),
                "persistence": entity_data.get("persistence", ""),
                "module": schema_data.get("generated_module", ""),
            })
            
            # Fields
            fields = entity_data.get("fields", {})
            for field_name, field_data in fields.items():
                field_id = self._generate_id("fld_")
                
                # Handle both dict and inline formats
                if isinstance(field_data, dict):
                    field_record = {
                        "_id": field_id,
                        "schema_id": schema_id,
                        "name": field_name,
                        "type": field_data.get("type", "str"),
                        "primary_key": field_data.get("primary_key", False),
                        "unique": field_data.get("unique", False),
                        "nullable": field_data.get("nullable", False),
                        "default": field_data.get("default"),
                    }
                    
                    # Handle enum
                    if "enum" in field_data:
                        field_record["type"] = "enum"
                        field_record["enum_values"] = ",".join(field_data["enum"])
                    
                    result["fields"].append(field_record)
                    
                    # Constraints
                    constraint_types = ["gt", "lt", "gte", "lte", "scale"]
                    for ct in constraint_types:
                        if ct in field_data:
                            result["field_constraints"].append({
                                "field_id": field_id,
                                "constraint_type": ct,
                                "value": str(field_data[ct]),
                            })
            
            # Ensures
            for ensure in entity_data.get("ensures", []):
                result["ensures"].append({
                    "schema_id": schema_id,
                    "name": ensure.get("name", ""),
                    "field": ensure.get("field", ""),
                    "constraint": ensure.get("constraint", ""),
                    "value": str(ensure.get("value", "")),
                    "description": ensure.get("description", ""),
                })
            
            # Indexes
            for index in entity_data.get("indexes", []):
                result["indexes"].append({
                    "schema_id": schema_id,
                    "fields": ",".join(index.get("fields", [])),
                    "unique": index.get("unique", False),
                })
        
        return result


class ModelNormalizer(Normalizer):
    """
    Specialized normalizer for model registry files.
    
    Models are already fairly flat, but we normalize for consistency.
    """
    
    def normalize_models(self, models_data: dict) -> dict:
        """Normalize model registry into table format."""
        result = {
            "models": [],
            "model_capabilities": [],
        }
        
        models = models_data.get("models", [])
        
        for model in models:
            model_id = self._generate_id("mdl_")
            
            # Main model record
            model_record = {
                "_id": model_id,
                "id": model.get("id", ""),
                "api_name": model.get("api_name", ""),
                "provider": model.get("provider", ""),
                "context_window": model.get("context_window", 0),
                "input_cost": model.get("input_cost", 0),
                "output_cost": model.get("output_cost", 0),
                "reasoning_score": model.get("reasoning_score", 0),
                "coding_score": model.get("coding_score", 0),
                "speed_rating": model.get("speed_rating", 0),
                "maturity": model.get("maturity", ""),
            }
            result["models"].append(model_record)
            
            # Capabilities
            capability_fields = [
                "supports_function_calling",
                "supports_vision",
                "supports_json_mode",
            ]
            for cap in capability_fields:
                if model.get(cap):
                    result["model_capabilities"].append({
                        "model_id": model_id,
                        "capability": cap.replace("supports_", ""),
                        "enabled": True,
                    })
        
        return result
