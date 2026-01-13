"""Thin wrappers that call plotsmith and timesmith.

This module provides wrappers for plotting functionality.
Return figure objects and file paths.
"""

from pathlib import Path
from typing import Any, Optional, Union

import pandas as pd

# Try to import Smith libraries with graceful fallback
try:
    import plotsmith

    HAS_PLOTSMITH = True
except ImportError:
    HAS_PLOTSMITH = False
    plotsmith = None

try:
    import timesmith

    HAS_TIMESMITH = True
except ImportError:
    HAS_TIMESMITH = False
    timesmith = None


def plot_time_series(
    data: pd.DataFrame,
    x_column: str,
    y_columns: Union[str, list],
    title: Optional[str] = None,
    output_path: Optional[Union[str, Path]] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Create a time series plot.

    Delegates to plotsmith when available.

    Args:
        data: DataFrame with time series data
        x_column: Column name for x-axis (typically timestamp)
        y_columns: Column name(s) for y-axis
        title: Optional plot title
        output_path: Optional path to save figure
        **kwargs: Additional plotting arguments

    Returns:
        Dictionary with plot metadata and saved path if applicable
    """
    y_columns_list = [y_columns] if isinstance(y_columns, str) else y_columns

    # Try plotsmith first
    if HAS_PLOTSMITH and plotsmith is not None:
        try:
            plot_data = data.set_index(x_column)
            plot_data = (
                plot_data[y_columns_list[0]]
                if len(y_columns_list) == 1
                else plot_data[y_columns_list]
            )

            output_path_obj = Path(output_path) if output_path else None
            output_path_obj and output_path_obj.parent.mkdir(parents=True, exist_ok=True)

            plotsmith.plot_timeseries(
                plot_data,
                title=title,
                save_path=str(output_path) if output_path else None,
                **kwargs,
            )

            return {
                "type": "time_series",
                "x_column": x_column,
                "y_columns": y_columns_list,
                "title": title,
                "output_path": str(output_path) if output_path else None,
                "data_shape": data.shape,
            }
        except Exception:
            pass

    # Fallback: return metadata only
    result = {
        "type": "time_series",
        "x_column": x_column,
        "y_columns": y_columns_list,
        "title": title,
        "data_shape": data.shape,
    }

    if output_path:
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        result["output_path"] = str(output_path)

    return result


def plot_anomalies(
    data: pd.DataFrame,
    timestamp_column: str,
    value_column: str,
    anomaly_column: str,
    title: Optional[str] = None,
    output_path: Optional[Union[str, Path]] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Create an anomaly visualization plot.

    Note: plotsmith doesn't have plot_anomalies, so this returns metadata only.

    Args:
        data: DataFrame with time series and anomaly labels
        timestamp_column: Column name for timestamps
        value_column: Column name for values to plot
        anomaly_column: Column name for anomaly labels
        title: Optional plot title
        output_path: Optional path to save figure
        **kwargs: Additional plotting arguments

    Returns:
        Dictionary with plot metadata and saved path if applicable
    """
    result = {
        "type": "anomaly",
        "timestamp_column": timestamp_column,
        "value_column": value_column,
        "anomaly_column": anomaly_column,
        "title": title,
        "data_shape": data.shape,
    }

    if output_path:
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        result["output_path"] = str(output_path)

    return result


def plot_forecast(
    data: pd.DataFrame,
    timestamp_column: str,
    actual_column: str,
    forecast_column: str,
    title: Optional[str] = None,
    output_path: Optional[Union[str, Path]] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Create a forecast visualization plot.

    Uses timesmith.plot_forecast when available.

    Args:
        data: DataFrame with actual and forecasted values
        timestamp_column: Column name for timestamps
        actual_column: Column name for actual values
        forecast_column: Column name for forecasted values
        title: Optional plot title
        output_path: Optional path to save figure
        **kwargs: Additional plotting arguments

    Returns:
        Dictionary with plot metadata and saved path if applicable
    """
    # Try timesmith first
    if HAS_TIMESMITH and timesmith is not None:
        try:
            plot_data = data.set_index(timestamp_column)
            historical = plot_data[actual_column].dropna()
            forecast = plot_data[forecast_column].dropna()

            fig, ax = timesmith.plot_forecast(
                historical,
                forecast,
                title=title or "Forecast",
                **kwargs,
            )

            output_path_str = None
            if output_path:
                output_path_obj = Path(output_path)
                output_path_obj.parent.mkdir(parents=True, exist_ok=True)
                fig.savefig(output_path_obj)
                output_path_str = str(output_path)

            return {
                "type": "forecast",
                "timestamp_column": timestamp_column,
                "actual_column": actual_column,
                "forecast_column": forecast_column,
                "title": title,
                "output_path": output_path_str,
                "data_shape": data.shape,
            }
        except Exception:
            pass

    # Fallback: return metadata only
    result = {
        "type": "forecast",
        "timestamp_column": timestamp_column,
        "actual_column": actual_column,
        "forecast_column": forecast_column,
        "title": title,
        "data_shape": data.shape,
    }

    if output_path:
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        result["output_path"] = str(output_path)

    return result
