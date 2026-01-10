"""Typed configs per chapter.

This module provides user-friendly configuration objects that map to core contracts.
Uses pydantic for validation.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from gridsmith.core import DatasetSpec, FeatureSpec, MetricSpec, SplitSpec


class AMIAnomalyConfig(BaseModel):
    """Configuration for AMI anomaly detection (Chapter 1)."""

    input_path: str = Field(..., description="Path to input data file")
    output_dir: str = Field(..., description="Output directory for results")
    timestamp_column: str = Field(default="timestamp", description="Name of timestamp column")
    value_column: str = Field(default="consumption", description="Name of value column to analyze")
    meter_id_column: Optional[str] = Field(default="meter_id", description="Name of meter ID column")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("input_path")
    @classmethod
    def validate_input_path(cls, v: str) -> str:
        """Validate that input path exists."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Input path does not exist: {v}")
        return v

    def to_core_config(self) -> "Config":
        """Convert to core Config object."""
        from gridsmith.core.pipelines import Config

        # Create dataset spec
        dataset_spec = DatasetSpec(
            name="ami_anomaly",
            required_columns=[self.timestamp_column, self.value_column],
            optional_columns=[self.meter_id_column] if self.meter_id_column else [],
            timestamp_column=self.timestamp_column,
            id_column=self.meter_id_column,
        )

        # Create metric specs
        metric_specs = [
            MetricSpec(name="precision", type="anomaly", required=True),
            MetricSpec(name="recall", type="anomaly", required=True),
            MetricSpec(name="f1", type="anomaly", required=True),
        ]

        return Config(
            input_path=self.input_path,
            output_dir=self.output_dir,
            dataset_spec=dataset_spec,
            metric_specs=metric_specs,
            metadata=self.metadata,
        )


class OutageDetectionConfig(BaseModel):
    """Configuration for outage detection."""

    input_path: str = Field(..., description="Path to input data file")
    output_dir: str = Field(..., description="Output directory for results")
    timestamp_column: str = Field(default="timestamp", description="Name of timestamp column")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("input_path")
    @classmethod
    def validate_input_path(cls, v: str) -> str:
        """Validate that input path exists."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Input path does not exist: {v}")
        return v

    def to_core_config(self) -> "Config":
        """Convert to core Config object."""
        from gridsmith.core.pipelines import Config

        dataset_spec = DatasetSpec(
            name="outage_detection",
            required_columns=[self.timestamp_column],
            timestamp_column=self.timestamp_column,
        )

        return Config(
            input_path=self.input_path,
            output_dir=self.output_dir,
            dataset_spec=dataset_spec,
            metadata=self.metadata,
        )


class AssetDegradationConfig(BaseModel):
    """Configuration for asset degradation analysis."""

    input_path: str = Field(..., description="Path to input data file")
    output_dir: str = Field(..., description="Output directory for results")
    timestamp_column: str = Field(default="timestamp", description="Name of timestamp column")
    asset_id_column: str = Field(default="asset_id", description="Name of asset ID column")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("input_path")
    @classmethod
    def validate_input_path(cls, v: str) -> str:
        """Validate that input path exists."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Input path does not exist: {v}")
        return v

    def to_core_config(self) -> "Config":
        """Convert to core Config object."""
        from gridsmith.core.pipelines import Config

        dataset_spec = DatasetSpec(
            name="asset_degradation",
            required_columns=[self.timestamp_column, self.asset_id_column],
            timestamp_column=self.timestamp_column,
            id_column=self.asset_id_column,
        )

        return Config(
            input_path=self.input_path,
            output_dir=self.output_dir,
            dataset_spec=dataset_spec,
            metadata=self.metadata,
        )


class LoadShapeConfig(BaseModel):
    """Configuration for load shape analysis."""

    input_path: str = Field(..., description="Path to input data file")
    output_dir: str = Field(..., description="Output directory for results")
    timestamp_column: str = Field(default="timestamp", description="Name of timestamp column")
    consumption_column: str = Field(default="consumption", description="Name of consumption column")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("input_path")
    @classmethod
    def validate_input_path(cls, v: str) -> str:
        """Validate that input path exists."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Input path does not exist: {v}")
        return v

    def to_core_config(self) -> "Config":
        """Convert to core Config object."""
        from gridsmith.core.pipelines import Config

        dataset_spec = DatasetSpec(
            name="load_shape",
            required_columns=[self.timestamp_column, self.consumption_column],
            timestamp_column=self.timestamp_column,
        )

        return Config(
            input_path=self.input_path,
            output_dir=self.output_dir,
            dataset_spec=dataset_spec,
            metadata=self.metadata,
        )


class TemperatureLoadConfig(BaseModel):
    """Configuration for temperature-to-load modeling (Chapter 1)."""

    input_path: Optional[str] = Field(None, description="Path to input data file (optional, generates synthetic if not provided)")
    output_dir: str = Field(..., description="Output directory for results")
    timestamp_column: str = Field(default="Date", description="Name of timestamp column")
    temperature_column: str = Field(default="Temperature_C", description="Name of temperature column")
    load_column: str = Field(default="Load_MW", description="Name of load column")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata (for synthetic data generation)")

    def to_core_config(self) -> "Config":
        """Convert to core Config object."""
        from gridsmith.core.pipelines import Config

        dataset_spec = DatasetSpec(
            name="temperature_load",
            required_columns=[self.temperature_column, self.load_column],
            optional_columns=[self.timestamp_column],
            timestamp_column=self.timestamp_column if self.timestamp_column else None,
        )

        metric_specs = [
            MetricSpec(name="mse", type="regression", required=True),
            MetricSpec(name="r2", type="regression", required=True),
            MetricSpec(name="mae", type="regression", required=True),
        ]

        return Config(
            input_path=self.input_path or "",
            output_dir=self.output_dir,
            dataset_spec=dataset_spec,
            metric_specs=metric_specs,
            metadata=self.metadata,
        )


class LoadForecastingConfig(BaseModel):
    """Configuration for load forecasting (Chapter 4)."""

    input_path: str = Field(..., description="Path to input data file")
    output_dir: str = Field(..., description="Output directory for results")
    timestamp_column: str = Field(default="timestamp", description="Name of timestamp column")
    load_column: str = Field(default="Load_MW", description="Name of load column")
    forecast_horizon: int = Field(default=24, description="Number of hours to forecast")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("input_path")
    @classmethod
    def validate_input_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate that input path exists if provided."""
        if v:
            path = Path(v)
            if not path.exists():
                raise ValueError(f"Input path does not exist: {v}")
        return v

    def to_core_config(self) -> "Config":
        """Convert to core Config object."""
        from gridsmith.core.pipelines import Config

        dataset_spec = DatasetSpec(
            name="load_forecasting",
            required_columns=[self.timestamp_column, self.load_column],
            timestamp_column=self.timestamp_column,
        )

        metric_specs = [
            MetricSpec(name="mse", type="forecast", required=True),
            MetricSpec(name="mae", type="forecast", required=True),
            MetricSpec(name="rmse", type="forecast", required=True),
        ]

        metadata = self.metadata.copy()
        metadata["forecast_horizon"] = self.forecast_horizon

        return Config(
            input_path=self.input_path or "",
            output_dir=self.output_dir,
            dataset_spec=dataset_spec,
            metric_specs=metric_specs,
            metadata=metadata,
        )


class PredictiveMaintenanceConfig(BaseModel):
    """Configuration for predictive maintenance (Chapter 5)."""

    input_path: str = Field(..., description="Path to input data file")
    output_dir: str = Field(..., description="Output directory for results")
    feature_columns: Optional[List[str]] = Field(None, description="Feature columns (auto-detected if not provided)")
    contamination: float = Field(default=0.05, description="Expected contamination rate for anomaly detection")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("input_path")
    @classmethod
    def validate_input_path(cls, v: str) -> str:
        """Validate that input path exists."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Input path does not exist: {v}")
        return v

    def to_core_config(self) -> "Config":
        """Convert to core Config object."""
        from gridsmith.core.pipelines import Config

        dataset_spec = DatasetSpec(
            name="predictive_maintenance",
            required_columns=self.feature_columns or ["Temperature_C", "Vibration_g", "OilPressure_psi", "Load_kVA"],
            optional_columns=["Failure"],
        )

        metric_specs = [
            MetricSpec(name="precision", type="anomaly", required=True),
            MetricSpec(name="recall", type="anomaly", required=True),
            MetricSpec(name="f1", type="anomaly", required=True),
            MetricSpec(name="roc_auc", type="anomaly", required=False),
        ]

        metadata = self.metadata.copy()
        metadata["contamination"] = self.contamination

        return Config(
            input_path=self.input_path,
            output_dir=self.output_dir,
            dataset_spec=dataset_spec,
            metric_specs=metric_specs,
            metadata=metadata,
        )


class OutagePredictionConfig(BaseModel):
    """Configuration for outage prediction (Chapter 6)."""

    input_path: str = Field(..., description="Path to input data file")
    output_dir: str = Field(..., description="Output directory for results")
    feature_columns: Optional[List[str]] = Field(None, description="Feature columns (auto-detected if not provided)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("input_path")
    @classmethod
    def validate_input_path(cls, v: str) -> str:
        """Validate that input path exists."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Input path does not exist: {v}")
        return v

    def to_core_config(self) -> "Config":
        """Convert to core Config object."""
        from gridsmith.core.pipelines import Config

        dataset_spec = DatasetSpec(
            name="outage_prediction",
            required_columns=self.feature_columns or ["WindSpeed_mps", "Rainfall_mm", "TreeDensity", "AssetAge_years"],
            optional_columns=["Outage"],
        )

        metric_specs = [
            MetricSpec(name="precision", type="anomaly", required=True),
            MetricSpec(name="recall", type="anomaly", required=True),
            MetricSpec(name="f1", type="anomaly", required=True),
            MetricSpec(name="roc_auc", type="anomaly", required=False),
        ]

        return Config(
            input_path=self.input_path,
            output_dir=self.output_dir,
            dataset_spec=dataset_spec,
            metric_specs=metric_specs,
            metadata=self.metadata,
        )

