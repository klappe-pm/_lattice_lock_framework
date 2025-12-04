"""
Data transformers for the pipeline.

Transformers apply rules to convert extracted data into the target format.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
import json


class TransformType(Enum):
    """Types of transformations."""
    MAP = "map"
    FILTER = "filter"
    AGGREGATE = "aggregate"
    JOIN = "join"
    CUSTOM = "custom"


class ValidationStatus(Enum):
    """Status of validation."""
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    SKIPPED = "skipped"


@dataclass
class TransformationRule:
    """Rule defining how to transform data."""
    id: int
    name: str
    source_field: str
    target_field: str
    transform_type: TransformType
    transform_config: dict[str, Any]
    priority: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.priority < 0:
            raise ValueError("Priority must be non-negative")


@dataclass
class TransformedRecord:
    """Data record after transformation."""
    id: int
    source_record_id: int
    transformed_data: dict[str, Any]
    applied_rules: list[str]
    transformed_at: Optional[datetime] = None
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validation_errors: list[str] = field(default_factory=list)
    created_at: Optional[datetime] = None


class BaseTransformer(ABC):
    """Base class for all data transformers."""

    def __init__(self, rules: list[TransformationRule]) -> None:
        self.rules = sorted(
            [r for r in rules if r.is_active],
            key=lambda r: r.priority
        )
        self._records_transformed = 0

    @abstractmethod
    def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform the input data according to rules."""
        pass

    @property
    def records_transformed(self) -> int:
        """Return the number of records transformed."""
        return self._records_transformed


class MapTransformer(BaseTransformer):
    """Transformer that maps fields from source to target."""

    def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        """Apply mapping transformations."""
        result = data.copy()

        for rule in self.rules:
            if rule.transform_type != TransformType.MAP:
                continue

            if rule.source_field in data:
                value = data[rule.source_field]

                config = rule.transform_config
                if "uppercase" in config and config["uppercase"]:
                    value = str(value).upper()
                elif "lowercase" in config and config["lowercase"]:
                    value = str(value).lower()
                elif "prefix" in config:
                    value = f"{config['prefix']}{value}"
                elif "suffix" in config:
                    value = f"{value}{config['suffix']}"

                result[rule.target_field] = value

        self._records_transformed += 1
        return result


class FilterTransformer(BaseTransformer):
    """Transformer that filters records based on conditions."""

    def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        """Apply filter transformations."""
        for rule in self.rules:
            if rule.transform_type != TransformType.FILTER:
                continue

            if rule.source_field not in data:
                continue

            value = data[rule.source_field]
            config = rule.transform_config

            if "min_value" in config and value < config["min_value"]:
                return {}
            if "max_value" in config and value > config["max_value"]:
                return {}
            if "equals" in config and value != config["equals"]:
                return {}
            if "not_equals" in config and value == config["not_equals"]:
                return {}

        self._records_transformed += 1
        return data


class AggregateTransformer(BaseTransformer):
    """Transformer that aggregates data."""

    def __init__(self, rules: list[TransformationRule]) -> None:
        super().__init__(rules)
        self._aggregations: dict[str, list[Any]] = {}

    def transform(self, data: dict[str, Any]) -> dict[str, Any]:
        """Collect data for aggregation."""
        for rule in self.rules:
            if rule.transform_type != TransformType.AGGREGATE:
                continue

            if rule.source_field in data:
                key = rule.target_field
                if key not in self._aggregations:
                    self._aggregations[key] = []
                self._aggregations[key].append(data[rule.source_field])

        self._records_transformed += 1
        return data

    def get_aggregates(self) -> dict[str, Any]:
        """Get computed aggregates."""
        result = {}
        for rule in self.rules:
            if rule.transform_type != TransformType.AGGREGATE:
                continue

            key = rule.target_field
            values = self._aggregations.get(key, [])
            config = rule.transform_config

            if config.get("operation") == "sum":
                result[key] = sum(values)
            elif config.get("operation") == "avg":
                result[key] = sum(values) / len(values) if values else 0
            elif config.get("operation") == "count":
                result[key] = len(values)
            elif config.get("operation") == "min":
                result[key] = min(values) if values else None
            elif config.get("operation") == "max":
                result[key] = max(values) if values else None

        return result


class TransformationPipeline:
    """Pipeline that chains multiple transformers."""

    def __init__(self) -> None:
        self._transformers: list[BaseTransformer] = []
        self._next_id = 1

    def add_transformer(self, transformer: BaseTransformer) -> None:
        """Add a transformer to the pipeline."""
        self._transformers.append(transformer)

    def process(
        self,
        source_record_id: int,
        data: dict[str, Any],
    ) -> Optional[TransformedRecord]:
        """Process data through all transformers."""
        result = data
        applied_rules: list[str] = []

        for transformer in self._transformers:
            result = transformer.transform(result)
            if not result:
                return None

            for rule in transformer.rules:
                applied_rules.append(rule.name)

        record = TransformedRecord(
            id=self._next_id,
            source_record_id=source_record_id,
            transformed_data=result,
            applied_rules=applied_rules,
            transformed_at=datetime.utcnow(),
            validation_status=ValidationStatus.PENDING,
        )
        self._next_id += 1
        return record


__all__ = [
    "TransformType",
    "ValidationStatus",
    "TransformationRule",
    "TransformedRecord",
    "BaseTransformer",
    "MapTransformer",
    "FilterTransformer",
    "AggregateTransformer",
    "TransformationPipeline",
]
