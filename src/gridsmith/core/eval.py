"""Thin wrappers that call metrics from timesmith and anomsmith.

This module provides glue code for evaluation metrics.
Keep only glue code here; delegate actual metric computation to Smith libs.
"""

from typing import Any, Dict, List, Optional

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
    metrics: Optional[List[str]] = None,
) -> Dict[str, float]:
    """Compute regression metrics.

    Delegates to timesmith when available, otherwise computes locally.

    Args:
        actual: Actual values
        predicted: Predicted values
        metrics: List of metric names to compute (default: ['mse', 'mae', 'rmse', 'mape'])

    Returns:
        Dictionary of metric names to values
    """
    if metrics is None:
        metrics = ["mse", "mae", "rmse", "mape"]

    # Try to use timesmith if available
    if HAS_TIMESMITH and timesmith is not None:
        try:
            # Delegate to timesmith for regression metrics
            # Assuming timesmith has a compute_metrics function
            if hasattr(timesmith, "compute_regression_metrics"):
                return timesmith.compute_regression_metrics(actual, predicted, metrics)
            elif hasattr(timesmith, "metrics") and hasattr(timesmith.metrics, "regression"):
                return timesmith.metrics.regression(actual, predicted, metrics)
        except Exception:
            # Fall back to local computation if timesmith fails
            pass

    # Fallback: compute locally
    results: Dict[str, float] = {}
    errors = actual - predicted

    if "mse" in metrics:
        results["mse"] = float((errors ** 2).mean())
    if "mae" in metrics:
        results["mae"] = float(errors.abs().mean())
    if "rmse" in metrics:
        results["rmse"] = float((errors ** 2).mean() ** 0.5)
    if "mape" in metrics:
        mask = actual != 0
        if mask.any():
            results["mape"] = float((errors[mask] / actual[mask]).abs().mean() * 100)

    return results


def compute_anomaly_metrics(
    actual_labels: pd.Series,
    predicted_labels: pd.Series,
    scores: Optional[pd.Series] = None,
    metrics: Optional[List[str]] = None,
) -> Dict[str, float]:
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
    if metrics is None:
        metrics = ["precision", "recall", "f1"]

    # Try to use anomsmith if available
    if HAS_ANOMSMITH and anomsmith is not None:
        try:
            # Delegate to anomsmith for anomaly metrics
            if hasattr(anomsmith, "compute_metrics"):
                return anomsmith.compute_metrics(actual_labels, predicted_labels, scores, metrics)
            elif hasattr(anomsmith, "metrics") and hasattr(anomsmith.metrics, "anomaly"):
                return anomsmith.metrics.anomaly(actual_labels, predicted_labels, scores, metrics)
            elif hasattr(anomsmith, "evaluate"):
                return anomsmith.evaluate(actual_labels, predicted_labels, scores, metrics)
        except Exception:
            # Fall back to local computation if anomsmith fails
            pass

    # Fallback: compute locally using sklearn
    results: Dict[str, float] = {}
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        precision_score,
        recall_score,
    )

    if "accuracy" in metrics:
        results["accuracy"] = float(accuracy_score(actual_labels, predicted_labels))
    if "precision" in metrics:
        results["precision"] = float(precision_score(actual_labels, predicted_labels, zero_division=0))
    if "recall" in metrics:
        results["recall"] = float(recall_score(actual_labels, predicted_labels, zero_division=0))
    if "f1" in metrics:
        results["f1"] = float(f1_score(actual_labels, predicted_labels, zero_division=0))

    return results


def compute_forecast_metrics(
    actual: pd.Series,
    forecast: pd.Series,
    horizons: Optional[pd.Series] = None,
    metrics: Optional[List[str]] = None,
) -> Dict[str, float]:
    """Compute forecast evaluation metrics.

    Delegates to timesmith for forecast-specific metrics.

    Args:
        actual: Actual values
        forecast: Forecasted values
        horizons: Optional forecast horizons
        metrics: List of metric names to compute

    Returns:
        Dictionary of metric names to values
    """
    # Try to use timesmith if available
    if HAS_TIMESMITH and timesmith is not None:
        try:
            # Delegate to timesmith for forecast metrics
            if hasattr(timesmith, "compute_forecast_metrics"):
                return timesmith.compute_forecast_metrics(actual, forecast, horizons, metrics)
            elif hasattr(timesmith, "metrics") and hasattr(timesmith.metrics, "forecast"):
                return timesmith.metrics.forecast(actual, forecast, horizons, metrics)
            elif hasattr(timesmith, "evaluate_forecast"):
                return timesmith.evaluate_forecast(actual, forecast, horizons, metrics)
        except Exception:
            # Fall back to regression metrics if timesmith fails
            pass

    # Fallback: use regression metrics
    return compute_regression_metrics(actual, forecast, metrics)

