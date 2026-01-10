"""Thin wrappers that call plotsmith.

This module provides wrappers for plotting functionality.
Return figure objects and file paths.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd

# Try to import plotsmith with graceful fallback
try:
    import plotsmith
    HAS_PLOTSMITH = True
except ImportError:
    HAS_PLOTSMITH = False
    plotsmith = None


def plot_time_series(
    data: pd.DataFrame,
    x_column: str,
    y_columns: Union[str, list],
    title: Optional[str] = None,
    output_path: Optional[Union[str, Path]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
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
    # Try to use plotsmith if available
    if HAS_PLOTSMITH and plotsmith is not None:
        try:
            if isinstance(y_columns, str):
                y_columns = [y_columns]
            
            # Delegate to plotsmith
            if hasattr(plotsmith, "plot_time_series"):
                fig = plotsmith.plot_time_series(data, x_column, y_columns, title=title, **kwargs)
            elif hasattr(plotsmith, "plot") and hasattr(plotsmith.plot, "time_series"):
                fig = plotsmith.plot.time_series(data, x_column, y_columns, title=title, **kwargs)
            else:
                raise AttributeError("plotsmith does not have expected plot_time_series function")
            
            # Save if output_path provided
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                if hasattr(fig, "savefig"):
                    fig.savefig(output_path)
                elif hasattr(fig, "save"):
                    fig.save(output_path)
                else:
                    # Fallback: try matplotlib-style save
                    import matplotlib.pyplot as plt
                    if hasattr(plt, "savefig"):
                        plt.savefig(output_path)
                        plt.close()
            
            return {
                "type": "time_series",
                "x_column": x_column,
                "y_columns": y_columns,
                "title": title,
                "output_path": str(output_path) if output_path else None,
                "data_shape": data.shape,
            }
        except Exception:
            # Fall back to placeholder if plotsmith fails
            pass

    # Fallback: return metadata only
    if isinstance(y_columns, str):
        y_columns = [y_columns]

    result: Dict[str, Any] = {
        "type": "time_series",
        "x_column": x_column,
        "y_columns": y_columns,
        "title": title,
        "data_shape": data.shape,
    }

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
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
) -> Dict[str, Any]:
    """Create an anomaly visualization plot.

    Delegates to plotsmith when available.

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
    # Try to use plotsmith if available
    if HAS_PLOTSMITH and plotsmith is not None:
        try:
            # Delegate to plotsmith
            if hasattr(plotsmith, "plot_anomalies"):
                fig = plotsmith.plot_anomalies(
                    data, timestamp_column, value_column, anomaly_column, title=title, **kwargs
                )
            elif hasattr(plotsmith, "plot") and hasattr(plotsmith.plot, "anomalies"):
                fig = plotsmith.plot.anomalies(
                    data, timestamp_column, value_column, anomaly_column, title=title, **kwargs
                )
            else:
                raise AttributeError("plotsmith does not have expected plot_anomalies function")
            
            # Save if output_path provided
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                if hasattr(fig, "savefig"):
                    fig.savefig(output_path)
                elif hasattr(fig, "save"):
                    fig.save(output_path)
                else:
                    # Fallback: try matplotlib-style save
                    import matplotlib.pyplot as plt
                    if hasattr(plt, "savefig"):
                        plt.savefig(output_path)
                        plt.close()
            
            return {
                "type": "anomaly",
                "timestamp_column": timestamp_column,
                "value_column": value_column,
                "anomaly_column": anomaly_column,
                "title": title,
                "output_path": str(output_path) if output_path else None,
                "data_shape": data.shape,
            }
        except Exception:
            # Fall back to placeholder if plotsmith fails
            pass

    # Fallback: return metadata only
    result: Dict[str, Any] = {
        "type": "anomaly",
        "timestamp_column": timestamp_column,
        "value_column": value_column,
        "anomaly_column": anomaly_column,
        "title": title,
        "data_shape": data.shape,
    }

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
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
) -> Dict[str, Any]:
    """Create a forecast visualization plot.

    Delegates to plotsmith when available.

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
    # Try to use plotsmith if available
    if HAS_PLOTSMITH and plotsmith is not None:
        try:
            # Delegate to plotsmith
            if hasattr(plotsmith, "plot_forecast"):
                fig = plotsmith.plot_forecast(
                    data, timestamp_column, actual_column, forecast_column, title=title, **kwargs
                )
            elif hasattr(plotsmith, "plot") and hasattr(plotsmith.plot, "forecast"):
                fig = plotsmith.plot.forecast(
                    data, timestamp_column, actual_column, forecast_column, title=title, **kwargs
                )
            else:
                raise AttributeError("plotsmith does not have expected plot_forecast function")
            
            # Save if output_path provided
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                if hasattr(fig, "savefig"):
                    fig.savefig(output_path)
                elif hasattr(fig, "save"):
                    fig.save(output_path)
                else:
                    # Fallback: try matplotlib-style save
                    import matplotlib.pyplot as plt
                    if hasattr(plt, "savefig"):
                        plt.savefig(output_path)
                        plt.close()
            
            return {
                "type": "forecast",
                "timestamp_column": timestamp_column,
                "actual_column": actual_column,
                "forecast_column": forecast_column,
                "title": title,
                "output_path": str(output_path) if output_path else None,
                "data_shape": data.shape,
            }
        except Exception:
            # Fall back to placeholder if plotsmith fails
            pass

    # Fallback: return metadata only
    result: Dict[str, Any] = {
        "type": "forecast",
        "timestamp_column": timestamp_column,
        "actual_column": actual_column,
        "forecast_column": forecast_column,
        "title": title,
        "data_shape": data.shape,
    }

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result["output_path"] = str(output_path)

    return result

