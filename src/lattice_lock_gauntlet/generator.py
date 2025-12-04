import os
from pathlib import Path
from typing import List
from jinja2 import Environment, FileSystemLoader

from .parser import LatticeParser, EntityDefinition, EnsuresClause

class GauntletGenerator:
    def __init__(self, lattice_file: str, output_dir: str):
        self.parser = LatticeParser(lattice_file)
        self.output_dir = Path(output_dir)
        self.env = Environment(
            loader=FileSystemLoader(Path(__file__).parent / "templates")
        )

    def generate(self):
        entities = self.parser.parse()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        template = self.env.get_template("test_contract.py.j2")

        for entity in entities:
            test_file_content = self._generate_test_file(entity, template)
            output_file = self.output_dir / f"test_contract_{entity.name}.py"
            with open(output_file, "w") as f:
                f.write(test_file_content)

    def _generate_test_file(self, entity: EntityDefinition, template) -> str:
        tests = []
        for clause in entity.ensures:
            assertion = self._build_assertion(clause)
            tests.append({
                "name": clause.name,
                "description": clause.description,
                "constraint": f"{clause.constraint}: {clause.value}",
                "field": clause.field,
                "assertion": assertion
            })

        return template.render(
            entity_name=entity.name,
            tests=tests
        )

    def _build_assertion(self, clause: EnsuresClause) -> str:
        if clause.constraint == 'gt':
            return f"assert value > {clause.value}, f'Expected {clause.field} > {clause.value}, got {{value}}'"
        elif clause.constraint == 'lt':
            return f"assert value < {clause.value}, f'Expected {clause.field} < {clause.value}, got {{value}}'"
        elif clause.constraint == 'gte':
            return f"assert value >= {clause.value}, f'Expected {clause.field} >= {clause.value}, got {{value}}'"
        elif clause.constraint == 'lte':
            return f"assert value <= {clause.value}, f'Expected {clause.field} <= {clause.value}, got {{value}}'"
        elif clause.constraint == 'unique':
            # Uniqueness is hard to test on a single instance without context (DB, list of others).
            # For now, we'll generate a placeholder or a property-based test hint.
            # In a real Gauntlet, this would check against a dataset fixture.
            return f"# Uniqueness check requires a collection context.\n        # assert is_unique(value, collection)"
        
        return "pass # Unknown constraint"
