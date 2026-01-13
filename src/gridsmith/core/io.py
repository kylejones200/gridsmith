"""I/O utilities for loading and saving data."""

from pathlib import Path
from typing import Any, Optional

import pandas as pd


def load_csv(
    path: str | Path, timestamp_column: Optional[str] = None, **kwargs: Any
) -> pd.DataFrame:
    """Load CSV file.

    Args:
        path: Path to CSV file
        timestamp_column: Optional column name to parse as datetime
        **kwargs: Additional arguments passed to pd.read_csv

    Returns:
        DataFrame with loaded data
    """
    df = pd.read_csv(path, **kwargs)
    return (
        df.assign(**{timestamp_column: pd.to_datetime(df[timestamp_column])})
        if timestamp_column and timestamp_column in df.columns
        else df
    )


def load_parquet(
    path: str | Path, timestamp_column: Optional[str] = None, **kwargs: Any
) -> pd.DataFrame:
    """Load Parquet file.

    Args:
        path: Path to Parquet file
        timestamp_column: Optional column name to parse as datetime
        **kwargs: Additional arguments passed to pd.read_parquet

    Returns:
        DataFrame with loaded data
    """
    df = pd.read_parquet(path, **kwargs)
    return (
        df.assign(**{timestamp_column: pd.to_datetime(df[timestamp_column])})
        if timestamp_column and timestamp_column in df.columns
        else df
    )


def save_dataframe(
    df: pd.DataFrame,
    path: str | Path,
    format: str = "parquet",
    **kwargs: Any,
) -> None:
    """Save DataFrame to file.

    Args:
        df: DataFrame to save
        path: Output path
        format: File format ('parquet', 'csv', or 'json')
        **kwargs: Additional arguments passed to save function
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    save_funcs = {
        "parquet": lambda: df.to_parquet(path, **kwargs),
        "csv": lambda: df.to_csv(path, index=False, **kwargs),
        "json": lambda: df.to_json(path, orient="records", **kwargs),
    }

    save_func = save_funcs.get(format)
    save_func and save_func()


def save_json(data: dict[str, Any], path: str | Path) -> None:
    """Save dictionary to JSON file.

    Args:
        data: Dictionary to save
        path: Output path
    """
    import json

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
