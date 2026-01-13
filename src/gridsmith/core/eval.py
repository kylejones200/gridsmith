"""Thin wrappers that call metrics from timesmith and anomsmith.

This module provides glue code for evaluation metrics.
Keep only glue code here; delegate actual metric computation to Smith libs.
"""

from typing import Optional

import pandas as pd

# Try to import Smith libraries with graceful fallback
try:
    import timesmith

    HAS_TIMESMITH = True
except ImportError:
    HAS_TIMESMITH = False
    timesmith = None

try:
    import anomsmith

    HAS_ANOMSMITH = True
except ImportError:
    HAS_ANOMSMITH = False
    anomsmith = None


def compute_regression_metrics(
    actual: pd.Series,
    predicted: pd.Series,
    metrics: Optional[list[str]] = None,
) -> dict[str, float]:
    """Compute regression metrics.

    Delegates to timesmith when available, otherwise computes locally.

    Args:
        actual: Actual values
        predicted: Predicted values
        metrics: List of metric names to compute (default: ['mse', 'mae', 'rmse', 'mape'])

    Returns:
        Dictionary of metric names to values
    """
    metrics = metrics or ["mse", "mae", "rmse", "mape"]
    errors = actual - predicted
    errors_squared = errors**2

    # Metric computation functions (vectorized)
    metric_computers = {
        "mse": lambda: float(errors_squared.mean()),
        "mae": lambda: float(errors.abs().mean()),
        "rmse": lambda: float(errors_squared.mean() ** 0.5),
        "mape": lambda: float(
            (errors[actual != 0] / actual[actual != 0]).abs().mean() * 100
        )
        if (actual != 0).any()
        else 0.0,
    }

    # Try timesmith first for supported metrics
    timesmith_metrics = {"mae", "rmse", "mape"}
    results = {}
    timesmith_available = HAS_TIMESMITH and timesmith is not None

    # Map timesmith functions
    timesmith_funcs = {
        "mae": getattr(timesmith, "mae", None),
        "rmse": getattr(timesmith, "rmse", None),
        "mape": getattr(timesmith, "mape", None),
    }

    # Compute metrics using timesmith where available
    for metric in metrics:
        if metric in timesmith_metrics and timesmith_available:
            func = timesmith_funcs.get(metric)
            if func:
                try:
                    results[metric] = float(func(actual, predicted))
                    continue
                except Exception as e:
                    # Fallback to local computation if timesmith fails
                    if metric in metric_computers:
                        results[metric] = metric_computers[metric]()
                    else:
                        raise RuntimeError(f"Timesmith metric computation failed for {metric} and no fallback available: {e}") from e
                    continue
        # Fallback to local computation
        if metric in metric_computers:
            results[metric] = metric_computers[metric]()

    return results


def compute_anomaly_metrics(
    actual_labels: pd.Series,
    predicted_labels: pd.Series,
    scores: Optional[pd.Series] = None,
    metrics: Optional[list[str]] = None,
) -> dict[str, float]:
    """Compute anomaly detection metrics.

    Delegates to anomsmith when available, otherwise computes locally.

    Args:
        actual_labels: True anomaly labels (binary)
        predicted_labels: Predicted anomaly labels (binary)
        scores: Optional anomaly scores
        metrics: List of metric names to compute (default: ['precision', 'recall', 'f1'])

    Returns:
        Dictionary of metric names to values
    """
    metrics = metrics or ["precision", "recall", "f1"]

    # Try anomsmith first
    if HAS_ANOMSMITH and anomsmith is not None:
        anomsmith_methods = [
            getattr(anomsmith, "compute_metrics", None),
            getattr(getattr(anomsmith, "metrics", None), "anomaly", None),
            getattr(anomsmith, "evaluate", None),
        ]
        errors = []
        for method in anomsmith_methods:
            if method:
                try:
                    return method(actual_labels, predicted_labels, scores, metrics)
                except Exception as e:
                    errors.append(e)
                    continue

        # Fallback: compute locally using sklearn
        if errors:
            error_msgs = "; ".join([str(e) for e in errors])
            # Log that anomsmith failed but continue with fallback
            import warnings
            warnings.warn(f"Anomsmith metric computation failed, using fallback: {error_msgs}")
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        precision_score,
        recall_score,
    )

    metric_funcs = {
        "accuracy": lambda: float(accuracy_score(actual_labels, predicted_labels)),
        "precision": lambda: float(
            precision_score(actual_labels, predicted_labels, zero_division=0)
        ),
        "recall": lambda: float(
            recall_score(actual_labels, predicted_labels, zero_division=0)
        ),
        "f1": lambda: float(
            f1_score(actual_labels, predicted_labels, zero_division=0)
        ),
    }

    return {
        metric: metric_funcs[metric]() for metric in metrics if metric in metric_funcs
    }


def compute_forecast_metrics(
    actual: pd.Series,
    forecast: pd.Series,
    horizons: Optional[pd.Series] = None,
    metrics: Optional[list[str]] = None,
) -> dict[str, float]:
    """Compute forecast evaluation metrics.

    Uses regression metrics (forecast metrics are the same as regression metrics).

    Args:
        actual: Actual values
        forecast: Forecasted values
        horizons: Optional forecast horizons (not used, kept for API compatibility)
        metrics: List of metric names to compute

    Returns:
        Dictionary of metric names to values
    """
    return compute_regression_metrics(actual, forecast, metrics)
