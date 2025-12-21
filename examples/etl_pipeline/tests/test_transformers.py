"""
Tests for data transformers.

Validates transformer functionality and rule application.
"""

import pytest

from src.transformers import (
    AggregateTransformer,
    FilterTransformer,
    MapTransformer,
    TransformationPipeline,
    TransformationRule,
    TransformedRecord,
    TransformType,
)


class TestTransformationRule:
    """Tests for TransformationRule model."""

    def test_valid_rule(self) -> None:
        """Test creating a valid transformation rule."""
        rule = TransformationRule(
            id=1,
            name="uppercase_name",
            source_field="name",
            target_field="NAME",
            transform_type=TransformType.MAP,
            transform_config={"uppercase": True},
        )
        assert rule.name == "uppercase_name"
        assert rule.transform_type == TransformType.MAP

    def test_negative_priority_rejected(self) -> None:
        """Test that negative priority is rejected."""
        with pytest.raises(ValueError, match="non-negative"):
            TransformationRule(
                id=1,
                name="test",
                source_field="a",
                target_field="b",
                transform_type=TransformType.MAP,
                transform_config={},
                priority=-1,
            )


class TestMapTransformer:
    """Tests for MapTransformer."""

    def test_simple_mapping(self) -> None:
        """Test simple field mapping."""
        rule = TransformationRule(
            id=1,
            name="copy_name",
            source_field="name",
            target_field="full_name",
            transform_type=TransformType.MAP,
            transform_config={},
        )
        transformer = MapTransformer([rule])

        result = transformer.transform({"name": "John"})

        assert result["full_name"] == "John"

    def test_uppercase_transform(self) -> None:
        """Test uppercase transformation."""
        rule = TransformationRule(
            id=1,
            name="uppercase",
            source_field="name",
            target_field="NAME",
            transform_type=TransformType.MAP,
            transform_config={"uppercase": True},
        )
        transformer = MapTransformer([rule])

        result = transformer.transform({"name": "john"})

        assert result["NAME"] == "JOHN"

    def test_lowercase_transform(self) -> None:
        """Test lowercase transformation."""
        rule = TransformationRule(
            id=1,
            name="lowercase",
            source_field="name",
            target_field="name_lower",
            transform_type=TransformType.MAP,
            transform_config={"lowercase": True},
        )
        transformer = MapTransformer([rule])

        result = transformer.transform({"name": "JOHN"})

        assert result["name_lower"] == "john"

    def test_prefix_transform(self) -> None:
        """Test prefix transformation."""
        rule = TransformationRule(
            id=1,
            name="add_prefix",
            source_field="id",
            target_field="prefixed_id",
            transform_type=TransformType.MAP,
            transform_config={"prefix": "USER_"},
        )
        transformer = MapTransformer([rule])

        result = transformer.transform({"id": "123"})

        assert result["prefixed_id"] == "USER_123"


class TestFilterTransformer:
    """Tests for FilterTransformer."""

    def test_min_value_filter(self) -> None:
        """Test minimum value filter."""
        rule = TransformationRule(
            id=1,
            name="min_age",
            source_field="age",
            target_field="age",
            transform_type=TransformType.FILTER,
            transform_config={"min_value": 18},
        )
        transformer = FilterTransformer([rule])

        assert transformer.transform({"age": 20}) == {"age": 20}
        assert transformer.transform({"age": 15}) == {}

    def test_max_value_filter(self) -> None:
        """Test maximum value filter."""
        rule = TransformationRule(
            id=1,
            name="max_price",
            source_field="price",
            target_field="price",
            transform_type=TransformType.FILTER,
            transform_config={"max_value": 100},
        )
        transformer = FilterTransformer([rule])

        assert transformer.transform({"price": 50}) == {"price": 50}
        assert transformer.transform({"price": 150}) == {}

    def test_equals_filter(self) -> None:
        """Test equals filter."""
        rule = TransformationRule(
            id=1,
            name="status_active",
            source_field="status",
            target_field="status",
            transform_type=TransformType.FILTER,
            transform_config={"equals": "active"},
        )
        transformer = FilterTransformer([rule])

        assert transformer.transform({"status": "active"}) == {"status": "active"}
        assert transformer.transform({"status": "inactive"}) == {}


class TestAggregateTransformer:
    """Tests for AggregateTransformer."""

    def test_sum_aggregation(self) -> None:
        """Test sum aggregation."""
        rule = TransformationRule(
            id=1,
            name="sum_values",
            source_field="value",
            target_field="total",
            transform_type=TransformType.AGGREGATE,
            transform_config={"operation": "sum"},
        )
        transformer = AggregateTransformer([rule])

        transformer.transform({"value": 10})
        transformer.transform({"value": 20})
        transformer.transform({"value": 30})

        aggregates = transformer.get_aggregates()
        assert aggregates["total"] == 60

    def test_avg_aggregation(self) -> None:
        """Test average aggregation."""
        rule = TransformationRule(
            id=1,
            name="avg_values",
            source_field="value",
            target_field="average",
            transform_type=TransformType.AGGREGATE,
            transform_config={"operation": "avg"},
        )
        transformer = AggregateTransformer([rule])

        transformer.transform({"value": 10})
        transformer.transform({"value": 20})
        transformer.transform({"value": 30})

        aggregates = transformer.get_aggregates()
        assert aggregates["average"] == 20

    def test_count_aggregation(self) -> None:
        """Test count aggregation."""
        rule = TransformationRule(
            id=1,
            name="count_records",
            source_field="id",
            target_field="count",
            transform_type=TransformType.AGGREGATE,
            transform_config={"operation": "count"},
        )
        transformer = AggregateTransformer([rule])

        transformer.transform({"id": 1})
        transformer.transform({"id": 2})
        transformer.transform({"id": 3})

        aggregates = transformer.get_aggregates()
        assert aggregates["count"] == 3


class TestTransformationPipeline:
    """Tests for TransformationPipeline."""

    def test_pipeline_processes_data(self) -> None:
        """Test that pipeline processes data through transformers."""
        rule = TransformationRule(
            id=1,
            name="uppercase",
            source_field="name",
            target_field="NAME",
            transform_type=TransformType.MAP,
            transform_config={"uppercase": True},
        )
        transformer = MapTransformer([rule])

        pipeline = TransformationPipeline()
        pipeline.add_transformer(transformer)

        result = pipeline.process(1, {"name": "john"})

        assert result is not None
        assert isinstance(result, TransformedRecord)
        assert result.transformed_data["NAME"] == "JOHN"

    def test_pipeline_returns_none_for_filtered_data(self) -> None:
        """Test that pipeline returns None for filtered data."""
        rule = TransformationRule(
            id=1,
            name="filter",
            source_field="age",
            target_field="age",
            transform_type=TransformType.FILTER,
            transform_config={"min_value": 18},
        )
        transformer = FilterTransformer([rule])

        pipeline = TransformationPipeline()
        pipeline.add_transformer(transformer)

        result = pipeline.process(1, {"age": 15})

        assert result is None
