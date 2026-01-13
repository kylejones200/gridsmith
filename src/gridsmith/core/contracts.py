"""Define canonical column names and schema checks.

This module defines domain objects, specs, and data contracts.
Core owns data contracts and orchestration logic.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


# Canonical column names for common grid data concepts
class Columns:
    """Canonical column name constants."""

    # Time columns
    TIMESTAMP = "timestamp"
    DATETIME = "datetime"
    TIME = "time"
    DATE = "date"

    # Identifier columns
    METER_ID = "meter_id"
    AMI_ID = "ami_id"
    ASSET_ID = "asset_id"
    LOCATION_ID = "location_id"
    CUSTOMER_ID = "customer_id"

    # Measurement columns
    DEMAND = "demand"
    CONSUMPTION = "consumption"
    VOLTAGE = "voltage"
    CURRENT = "current"
    POWER = "power"
    ENERGY = "energy"
    FREQUENCY = "frequency"

    # Anomaly columns
    IS_ANOMALY = "is_anomaly"
    ANOMALY_SCORE = "anomaly_score"
    ANOMALY_TYPE = "anomaly_type"

    # Location columns
    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    GEOJSON = "geojson"

    # Event columns
    EVENT_START = "event_start"
    EVENT_END = "event_end"
    EVENT_TYPE = "event_type"
    EVENT_SEVERITY = "event_severity"

    # Forecast columns
    FORECAST = "forecast"
    ACTUAL = "actual"
    FORECAST_LOWER = "forecast_lower"
    FORECAST_UPPER = "forecast_upper"
    HORIZON = "horizon"


@dataclass
class DatasetSpec:
    """Specification for a dataset schema and requirements."""

    name: str
    required_columns: list[str]
    optional_columns: list[str] = field(default_factory=list)
    timestamp_column: Optional[str] = None
    id_column: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self, df_columns: set[str]) -> list[str]:
        """Validate that a DataFrame has required columns.

        Args:
            df_columns: Set of column names in the DataFrame

        Returns:
            List of missing required columns
        """
        missing = set(self.required_columns) - df_columns
        return sorted(missing)


@dataclass
class FeatureSpec:
    """Specification for features used in modeling."""

    name: str
    type: str  # 'numeric', 'categorical', 'datetime', 'geospatial', 'text'
    required: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SplitSpec:
    """Specification for train/test/validation splits."""

    train_start: Optional[str] = None
    train_end: Optional[str] = None
    test_start: Optional[str] = None
    test_end: Optional[str] = None
    validation_start: Optional[str] = None
    validation_end: Optional[str] = None
    train_ratio: Optional[float] = None
    test_ratio: Optional[float] = None
    validation_ratio: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSpec:
    """Specification for evaluation metrics."""

    name: str
    type: str  # 'regression', 'classification', 'anomaly', 'forecast'
    params: dict[str, Any] = field(default_factory=dict)
    required: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


def validate_schema(df_columns: set[str], spec: DatasetSpec) -> None:
    """Validate DataFrame schema against a DatasetSpec.

    Args:
        df_columns: Set of column names in the DataFrame
        spec: DatasetSpec to validate against

    Raises:
        ValueError: If required columns are missing
    """
    missing = spec.validate(df_columns)
    if missing:
        raise ValueError(
            f"Missing required columns for {spec.name}: {', '.join(missing)}"
        )
