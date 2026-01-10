"""Typed results per chapter.

This module provides structured result objects for API responses.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class AMIAnomalyResults:
    """Results from AMI anomaly detection."""

    metrics: Dict[str, float]
    output_dir: str
    tables: Dict[str, str] = field(default_factory=dict)
    figures: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

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

    metrics: Dict[str, float]
    output_dir: str
    tables: Dict[str, str] = field(default_factory=dict)
    figures: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetDegradationResults:
    """Results from asset degradation analysis."""

    metrics: Dict[str, float]
    output_dir: str
    tables: Dict[str, str] = field(default_factory=dict)
    figures: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadShapeResults:
    """Results from load shape analysis."""

    metrics: Dict[str, float]
    output_dir: str
    tables: Dict[str, str] = field(default_factory=dict)
    figures: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TemperatureLoadResults:
    """Results from temperature-to-load modeling (Chapter 1)."""

    metrics: Dict[str, float]
    output_dir: str
    tables: Dict[str, str] = field(default_factory=dict)
    figures: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadForecastingResults:
    """Results from load forecasting (Chapter 4)."""

    metrics: Dict[str, float]
    output_dir: str
    tables: Dict[str, str] = field(default_factory=dict)
    figures: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictiveMaintenanceResults:
    """Results from predictive maintenance (Chapter 5)."""

    metrics: Dict[str, float]
    output_dir: str
    tables: Dict[str, str] = field(default_factory=dict)
    figures: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutagePredictionResults:
    """Results from outage prediction (Chapter 6)."""

    metrics: Dict[str, float]
    output_dir: str
    tables: Dict[str, str] = field(default_factory=dict)
    figures: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

