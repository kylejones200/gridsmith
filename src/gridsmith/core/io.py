"""Loaders for common utility formats.

This module provides data loading utilities for CSV, parquet, JSON, and GeoJSON.
No remote fetch in core unless it stays optional and isolated.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd


def load_csv(
    path: Union[str, Path],
    timestamp_column: Optional[str] = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame.

    Args:
        path: Path to CSV file
        timestamp_column: Optional column name to parse as datetime
        **kwargs: Additional arguments passed to pd.read_csv

    Returns:
        DataFrame with loaded data
    """
    df = pd.read_csv(path, **kwargs)
    if timestamp_column and timestamp_column in df.columns:
        df[timestamp_column] = pd.to_datetime(df[timestamp_column])
    return df


def load_parquet(
    path: Union[str, Path],
    timestamp_column: Optional[str] = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """Load a Parquet file into a pandas DataFrame.

    Args:
        path: Path to Parquet file
        timestamp_column: Optional column name to parse as datetime
        **kwargs: Additional arguments passed to pd.read_parquet

    Returns:
        DataFrame with loaded data
    """
    df = pd.read_parquet(path, **kwargs)
    if timestamp_column and timestamp_column in df.columns:
        df[timestamp_column] = pd.to_datetime(df[timestamp_column])
    return df


def load_json(
    path: Union[str, Path],
    **kwargs: Any,
) -> Dict[str, Any]:
    """Load a JSON file.

    Args:
        path: Path to JSON file
        **kwargs: Additional arguments passed to json.load

    Returns:
        Dictionary with loaded JSON data
    """
    with open(path, "r") as f:
        return json.load(f, **kwargs)


def load_geojson(
    path: Union[str, Path],
    **kwargs: Any,
) -> Dict[str, Any]:
    """Load a GeoJSON file.

    Args:
        path: Path to GeoJSON file
        **kwargs: Additional arguments (reserved for future use)

    Returns:
        Dictionary with loaded GeoJSON data
    """
    with open(path, "r") as f:
        return json.load(f, **kwargs)


def save_dataframe(
    df: pd.DataFrame,
    path: Union[str, Path],
    format: str = "parquet",
    **kwargs: Any,
) -> None:
    """Save a DataFrame to disk.

    Args:
        df: DataFrame to save
        path: Output path
        format: Output format ('parquet', 'csv', or 'json')
        **kwargs: Additional arguments passed to save method
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if format == "parquet":
        df.to_parquet(path, **kwargs)
    elif format == "csv":
        df.to_csv(path, **kwargs)
    elif format == "json":
        df.to_json(path, orient="records", **kwargs)
    else:
        raise ValueError(f"Unsupported format: {format}")


def save_json(
    data: Dict[str, Any],
    path: Union[str, Path],
    **kwargs: Any,
) -> None:
    """Save a dictionary to JSON file.

    Args:
        data: Dictionary to save
        path: Output path
        **kwargs: Additional arguments passed to json.dump
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        json.dump(data, f, indent=2, **kwargs)

