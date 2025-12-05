import yaml
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

@dataclass
class EnsuresClause:
    name: str
    field: str
    constraint: str
    value: Any
    description: str

@dataclass
class EntityDefinition:
    name: str
    fields: Dict[str, Any]
    ensures: List[EnsuresClause]

class LatticeParser:
    def __init__(self, lattice_file: str):
        self.lattice_file = lattice_file
        self.entities: List[EntityDefinition] = []

    def parse(self) -> List[EntityDefinition]:
        with open(self.lattice_file, 'r') as f:
            data = yaml.safe_load(f)

        if 'entities' not in data:
            return []

        for entity_name, entity_def in data['entities'].items():
            self.entities.append(self._parse_entity(entity_name, entity_def))

        return self.entities

    def _parse_entity(self, name: str, definition: Dict[str, Any]) -> EntityDefinition:
        ensures = []
        fields = definition.get('fields', {})

        # Parse implicit ensures from field constraints
        for field_name, field_def in fields.items():
            ensures.extend(self._extract_field_constraints(field_name, field_def))

        # Parse explicit ensures
        if 'ensures' in definition:
            for clause in definition['ensures']:
                # Expecting format: { description: "...", check: "expression" } or similar
                # For now, let's assume a simple list of dicts with 'name', 'check', 'description'
                # Or maybe the prompt implies something else? "Extract ensures clauses"
                # Let's support a generic structure for now.
                if isinstance(clause, dict):
                    ensures.append(EnsuresClause(
                        name=clause.get('name', 'unnamed_rule'),
                        field=clause.get('field', 'global'),
                        constraint=clause.get('constraint', 'custom'),
                        value=clause.get('value', None),
                        description=clause.get('description', 'Custom rule')
                    ))

        return EntityDefinition(name=name, fields=fields, ensures=ensures)

    def _extract_field_constraints(self, field_name: str, field_def: Dict[str, Any]) -> List[EnsuresClause]:
        constraints = []
        
        # Numeric constraints
        if 'gt' in field_def:
            constraints.append(EnsuresClause(
                name=f"{field_name}_gt_{field_def['gt']}".replace('.', '_'),
                field=field_name,
                constraint='gt',
                value=field_def['gt'],
                description=f"Ensure {field_name} > {field_def['gt']}"
            ))
        if 'lt' in field_def:
            constraints.append(EnsuresClause(
                name=f"{field_name}_lt_{field_def['lt']}".replace('.', '_'),
                field=field_name,
                constraint='lt',
                value=field_def['lt'],
                description=f"Ensure {field_name} < {field_def['lt']}"
            ))
        if 'gte' in field_def:
            constraints.append(EnsuresClause(
                name=f"{field_name}_gte_{field_def['gte']}".replace('.', '_'),
                field=field_name,
                constraint='gte',
                value=field_def['gte'],
                description=f"Ensure {field_name} >= {field_def['gte']}"
            ))
        if 'lte' in field_def:
            constraints.append(EnsuresClause(
                name=f"{field_name}_lte_{field_def['lte']}".replace('.', '_'),
                field=field_name,
                constraint='lte',
                value=field_def['lte'],
                description=f"Ensure {field_name} <= {field_def['lte']}"
            ))

        # Uniqueness
        if field_def.get('unique') is True:
             constraints.append(EnsuresClause(
                name=f"{field_name}_unique",
                field=field_name,
                constraint='unique',
                value=True,
                description=f"Ensure {field_name} is unique"
            ))

        return constraints
