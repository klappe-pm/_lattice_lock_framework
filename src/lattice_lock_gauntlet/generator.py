import os
from pathlib import Path
from typing import List
from jinja2 import Environment, FileSystemLoader

from .parser import LatticeParser, EntityDefinition, EnsuresClause

class GauntletGenerator:
    """
    Generates pytest test contracts from Lattice Lock definitions.

    Attributes:
        parser (LatticeParser): The parser for reading lattice definitions.
        output_dir (Path): Directory where generated tests will be saved.
        env (Environment): Jinja2 environment for template loading.
    """
    def __init__(self, lattice_file: str, output_dir: str):
        self.parser = LatticeParser(lattice_file)
        self.output_dir = Path(output_dir)
        self.env = Environment(
            loader=FileSystemLoader(Path(__file__).parent / "templates")
        )

    def generate(self):
        """Generates test files for all parsed entities."""
        entities = self.parser.parse()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        template = self.env.get_template("test_contract.py.j2")

        for entity in entities:
            test_file_content = self._generate_test_file(entity, template)
            output_file = self.output_dir / f"test_contract_{entity.name}.py"
            with open(output_file, "w") as f:
                f.write(test_file_content)

    def _generate_test_file(self, entity: EntityDefinition, template) -> str:
        """Generates content for a single test file."""
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

        # Generate boundary tests (placeholders for now)
        boundary_tests = []
        for clause in entity.ensures:
            if clause.constraint in ['gt', 'lt', 'gte', 'lte']:
                 boundary_tests.append({
                     "name": clause.name,
                     "field": clause.field,
                     "description": f"Verify boundary for {clause.constraint} {clause.value}"
                 })

        # Enrich fields with example values for the fixture
        fields_data = {}
        for fname, fdef in entity.fields.items():
            example = "None"
            if 'gt' in fdef: example = str(fdef['gt'] + 1)
            elif 'gte' in fdef: example = str(fdef['gte'])
            elif 'lt' in fdef: example = str(fdef['lt'] - 1)
            elif 'lte' in fdef: example = str(fdef['lte'])
            fields_data[fname] = {"example_value": example}

        return template.render(
            entity_name=entity.name,
            tests=tests,
            boundary_tests=boundary_tests,
            fields=fields_data
        )

    def _build_assertion(self, clause: EnsuresClause) -> str:
        """Builds a Python assertion string for a given clause."""
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
