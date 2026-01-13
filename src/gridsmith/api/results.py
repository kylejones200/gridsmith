"""Typed results per chapter.

This module provides structured result objects for API responses.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class AMIAnomalyResults:
    """Results from AMI anomaly detection."""

    metrics: dict[str, float]
    output_dir: str
    tables: dict[str, str] = field(default_factory=dict)
    figures: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def metrics_path(self) -> Path:
        """Path to metrics JSON file."""
        return Path(self.output_dir) / "metrics.json"

    @property
    def anomaly_results_table(self) -> Optional[Path]:
        """Path to anomaly results table."""
        table_path = self.tables.get("anomaly_results")
        return Path(table_path) if table_path else None

    @property
    def anomaly_plot(self) -> Optional[Path]:
        """Path to anomaly plot."""
        plot_path = self.figures.get("anomaly_plot")
        return Path(plot_path) if plot_path else None


@dataclass
class OutageDetectionResults:
    """Results from outage detection."""

    metrics: dict[str, float]
    output_dir: str
    tables: dict[str, str] = field(default_factory=dict)
    figures: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetDegradationResults:
    """Results from asset degradation analysis."""

    metrics: dict[str, float]
    output_dir: str
    tables: dict[str, str] = field(default_factory=dict)
    figures: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadShapeResults:
    """Results from load shape analysis."""

    metrics: dict[str, float]
    output_dir: str
    tables: dict[str, str] = field(default_factory=dict)
    figures: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TemperatureLoadResults:
    """Results from temperature-to-load modeling."""

    metrics: dict[str, float]
    output_dir: str
    tables: dict[str, str] = field(default_factory=dict)
    figures: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadForecastingResults:
    """Results from load forecasting."""

    metrics: dict[str, float]
    output_dir: str
    tables: dict[str, str] = field(default_factory=dict)
    figures: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictiveMaintenanceResults:
    """Results from predictive maintenance."""

    metrics: dict[str, float]
    output_dir: str
    tables: dict[str, str] = field(default_factory=dict)
    figures: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OutagePredictionResults:
    """Results from outage prediction."""

    metrics: dict[str, float]
    output_dir: str
    tables: dict[str, str] = field(default_factory=dict)
    figures: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
