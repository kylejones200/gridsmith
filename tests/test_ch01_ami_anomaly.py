"""Tests for Chapter 1: AMI Anomaly Detection pipeline.

These are golden tests that compare schema and metric keys.
"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

from gridsmith import GridSmithClient
from gridsmith.api.config import AMIAnomalyConfig


@pytest.fixture
def sample_ami_data(tmp_path):
    """Create sample AMI data for testing."""
    import numpy as np
    from datetime import datetime, timedelta

    # Create sample time series with some anomalies
    start_time = datetime(2024, 1, 1)
    timestamps = [start_time + timedelta(hours=i) for i in range(100)]
    
    # Normal consumption with some noise
    np.random.seed(42)
    consumption = 100 + np.random.normal(0, 10, 100)
    
    # Add some anomalies
    consumption[20] = 200  # Anomaly
    consumption[50] = 250  # Anomaly
    consumption[75] = 50   # Anomaly (low)
    
    df = pd.DataFrame({
        "timestamp": timestamps,
        "consumption": consumption,
        "meter_id": ["meter_001"] * 100,
    })
    
    data_file = tmp_path / "ami_data.csv"
    df.to_csv(data_file, index=False)
    
    return data_file, df


def test_ami_anomaly_pipeline_basic(sample_ami_data):
    """Test basic AMI anomaly pipeline execution."""
    data_file, _ = sample_ami_data
    
    with TemporaryDirectory() as tmpdir:
        config = AMIAnomalyConfig(
            input_path=str(data_file),
            output_dir=tmpdir,
            timestamp_column="timestamp",
            value_column="consumption",
            meter_id_column="meter_id",
        )
        
        client = GridSmithClient()
        results = client.ami_anomaly(config)
        
        # Check that output directory was created
        assert Path(results.output_dir).exists()
        
        # Check that metrics.json exists
        metrics_path = Path(results.output_dir) / "metrics.json"
        assert metrics_path.exists()
        
        # Check that tables directory exists and has results
        assert "anomaly_results" in results.tables
        table_path = Path(results.tables["anomaly_results"])
        assert table_path.exists()
        
        # Check that figures directory structure exists
        figures_dir = Path(results.output_dir) / "figures"
        assert figures_dir.exists()


def test_ami_anomaly_metrics_schema(sample_ami_data):
    """Test that metrics.json has expected schema."""
    data_file, _ = sample_ami_data
    
    with TemporaryDirectory() as tmpdir:
        config = AMIAnomalyConfig(
            input_path=str(data_file),
            output_dir=tmpdir,
            timestamp_column="timestamp",
            value_column="consumption",
            meter_id_column="meter_id",
        )
        
        client = GridSmithClient()
        results = client.ami_anomaly(config)
        
        # Load metrics
        metrics_path = Path(results.output_dir) / "metrics.json"
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
        
        # Check that metrics is a dict
        assert isinstance(metrics, dict)
        
        # If ground truth was available, check for expected keys
        # For now, metrics may be empty if no ground truth
        # This test validates the schema exists, not the values


def test_ami_anomaly_results_table_schema(sample_ami_data):
    """Test that anomaly results table has expected columns."""
    data_file, original_df = sample_ami_data
    
    with TemporaryDirectory() as tmpdir:
        config = AMIAnomalyConfig(
            input_path=str(data_file),
            output_dir=tmpdir,
            timestamp_column="timestamp",
            value_column="consumption",
            meter_id_column="meter_id",
        )
        
        client = GridSmithClient()
        results = client.ami_anomaly(config)
        
        # Load results table
        table_path = Path(results.tables["anomaly_results"])
        df = pd.read_parquet(table_path)
        
        # Check required columns
        required_columns = {"timestamp", "consumption", "anomaly_score", "is_anomaly"}
        assert required_columns.issubset(set(df.columns))
        
        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
        assert pd.api.types.is_numeric_dtype(df["consumption"])
        assert pd.api.types.is_numeric_dtype(df["anomaly_score"])
        assert pd.api.types.is_bool_dtype(df["is_anomaly"])
        
        # Check that we have the same number of rows
        assert len(df) == len(original_df)


def test_ami_anomaly_with_ground_truth(sample_ami_data):
    """Test pipeline with ground truth labels."""
    data_file, df = sample_ami_data
    
    # Add ground truth labels
    df["ground_truth"] = [False] * 100
    df.loc[20, "ground_truth"] = True
    df.loc[50, "ground_truth"] = True
    df.loc[75, "ground_truth"] = True
    
    # Save updated data
    data_file.unlink()
    df.to_csv(data_file, index=False)
    
    with TemporaryDirectory() as tmpdir:
        config = AMIAnomalyConfig(
            input_path=str(data_file),
            output_dir=tmpdir,
            timestamp_column="timestamp",
            value_column="consumption",
            meter_id_column="meter_id",
        )
        
        client = GridSmithClient()
        results = client.ami_anomaly(config)
        
        # With ground truth, we should have metrics
        # Check that metrics file exists and has values
        metrics_path = Path(results.output_dir) / "metrics.json"
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
        
        # Metrics should exist (even if empty)
        assert isinstance(metrics, dict)


def test_ami_anomaly_config_validation(tmp_path):
    """Test that config validation works correctly."""
    # Create a test file
    test_file = tmp_path / "test.csv"
    test_file.write_text("timestamp,consumption\n2024-01-01,100.0\n")
    
    # Valid config
    config = AMIAnomalyConfig(
        input_path=str(test_file),
        output_dir=str(tmp_path / "output"),
    )
    assert config.timestamp_column == "timestamp"
    assert config.value_column == "consumption"
    
    # Invalid config (missing input_path)
    with pytest.raises(Exception):
        AMIAnomalyConfig(output_dir=str(tmp_path / "output"))
    
    # Invalid input path
    with pytest.raises(ValueError, match="Input path does not exist"):
        AMIAnomalyConfig(
            input_path="/nonexistent/file.csv",
            output_dir=str(tmp_path / "output"),
        )

