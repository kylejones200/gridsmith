"""Tests for core contracts module."""

import pytest

from gridsmith.core.contracts import (
    Columns,
    DatasetSpec,
    FeatureSpec,
    MetricSpec,
    SplitSpec,
    validate_schema,
)


def test_columns_constants():
    """Test that column constants are defined."""
    assert Columns.TIMESTAMP == "timestamp"
    assert Columns.CONSUMPTION == "consumption"
    assert Columns.IS_ANOMALY == "is_anomaly"


def test_dataset_spec_validation():
    """Test DatasetSpec validation."""
    spec = DatasetSpec(
        name="test",
        required_columns=["col1", "col2"],
        optional_columns=["col3"],
    )
    
    # Valid schema
    df_columns = {"col1", "col2", "col3", "col4"}
    missing = spec.validate(df_columns)
    assert len(missing) == 0
    
    # Missing required column
    df_columns = {"col1"}
    missing = spec.validate(df_columns)
    assert "col2" in missing


def test_validate_schema():
    """Test validate_schema function."""
    spec = DatasetSpec(
        name="test",
        required_columns=["col1", "col2"],
    )
    
    # Valid
    validate_schema({"col1", "col2", "col3"}, spec)
    
    # Invalid
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_schema({"col1"}, spec)


def test_feature_spec():
    """Test FeatureSpec creation."""
    spec = FeatureSpec(
        name="consumption",
        type="numeric",
        required=True,
    )
    assert spec.name == "consumption"
    assert spec.type == "numeric"
    assert spec.required is True


def test_metric_spec():
    """Test MetricSpec creation."""
    spec = MetricSpec(
        name="f1",
        type="anomaly",
        required=True,
    )
    assert spec.name == "f1"
    assert spec.type == "anomaly"


def test_split_spec():
    """Test SplitSpec creation."""
    spec = SplitSpec(
        train_ratio=0.7,
        test_ratio=0.3,
    )
    assert spec.train_ratio == 0.7
    assert spec.test_ratio == 0.3

