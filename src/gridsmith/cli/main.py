"""CLI entrypoint using Typer.

This module provides command-line interface for running GridSmith pipelines.
"""

import json
from pathlib import Path
from typing import Optional

import typer
import yaml

from gridsmith.api.client import GridSmithClient
from gridsmith.api.config import (
    AMIAnomalyConfig,
    AssetDegradationConfig,
    LoadForecastingConfig,
    LoadShapeConfig,
    OutageDetectionConfig,
    OutagePredictionConfig,
    PredictiveMaintenanceConfig,
    TemperatureLoadConfig,
)

app = typer.Typer(
    name="gridsmith",
    help="GridSmith: Orchestration and reference app layer for ML4U chapter examples",
    add_completion=False,
)


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file.

    Args:
        config_path: Path to YAML config file

    Returns:
        Dictionary with configuration
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, "r") as f:
        if path.suffix in [".yaml", ".yml"]:
            return yaml.safe_load(f)
        elif path.suffix == ".json":
            return json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")


@app.command()
def run(
    pipeline: str = typer.Argument(..., help="Pipeline name"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config YAML file"),
):
    """Run a GridSmith pipeline."""
    if config is None:
        typer.echo("Error: --config is required", err=True)
        raise typer.Exit(1)

    config_dict = load_config(config)

    client = GridSmithClient()

    try:
        if pipeline == "ami-anomaly":
            config_obj = AMIAnomalyConfig(**config_dict)
            results = client.ami_anomaly(config_obj)
            typer.echo(f"✓ AMI anomaly detection completed")
            typer.echo(f"  Output directory: {results.output_dir}")
            typer.echo(f"  Metrics: {list(results.metrics.keys())}")
            typer.echo(f"  Tables: {list(results.tables.keys())}")
            typer.echo(f"  Figures: {list(results.figures.keys())}")

        elif pipeline == "temperature-load":
            config_obj = TemperatureLoadConfig(**config_dict)
            results = client.temperature_load(config_obj)
            typer.echo(f"✓ Temperature-to-load modeling completed")
            typer.echo(f"  Output directory: {results.output_dir}")
            typer.echo(f"  Metrics: {list(results.metrics.keys())}")

        elif pipeline == "load-forecasting":
            config_obj = LoadForecastingConfig(**config_dict)
            results = client.load_forecasting(config_obj)
            typer.echo(f"✓ Load forecasting completed")
            typer.echo(f"  Output directory: {results.output_dir}")
            typer.echo(f"  Metrics: {list(results.metrics.keys())}")

        elif pipeline == "predictive-maintenance":
            config_obj = PredictiveMaintenanceConfig(**config_dict)
            results = client.predictive_maintenance(config_obj)
            typer.echo(f"✓ Predictive maintenance completed")
            typer.echo(f"  Output directory: {results.output_dir}")
            typer.echo(f"  Metrics: {list(results.metrics.keys())}")

        elif pipeline == "outage-prediction":
            config_obj = OutagePredictionConfig(**config_dict)
            results = client.outage_prediction(config_obj)
            typer.echo(f"✓ Outage prediction completed")
            typer.echo(f"  Output directory: {results.output_dir}")
            typer.echo(f"  Metrics: {list(results.metrics.keys())}")

        elif pipeline == "outage-detect":
            config_obj = OutageDetectionConfig(**config_dict)
            results = client.outage_detection(config_obj)
            typer.echo(f"✓ Outage detection completed")
            typer.echo(f"  Output directory: {results.output_dir}")

        elif pipeline == "asset-degradation":
            config_obj = AssetDegradationConfig(**config_dict)
            results = client.asset_degradation(config_obj)
            typer.echo(f"✓ Asset degradation analysis completed")
            typer.echo(f"  Output directory: {results.output_dir}")

        elif pipeline == "load-shape":
            config_obj = LoadShapeConfig(**config_dict)
            results = client.load_shape(config_obj)
            typer.echo(f"✓ Load shape analysis completed")
            typer.echo(f"  Output directory: {results.output_dir}")

        else:
            typer.echo(f"Error: Unknown pipeline '{pipeline}'", err=True)
            typer.echo("Available pipelines:")
            typer.echo("  - ami-anomaly: AMI anomaly detection")
            typer.echo("  - temperature-load: Temperature-to-load modeling (Chapter 1)")
            typer.echo("  - load-forecasting: Load forecasting (Chapter 4)")
            typer.echo("  - predictive-maintenance: Predictive maintenance (Chapter 5)")
            typer.echo("  - outage-prediction: Outage prediction (Chapter 6)")
            typer.echo("  - outage-detect: Outage event detection")
            typer.echo("  - asset-degradation: Asset degradation analysis")
            typer.echo("  - load-shape: Load shape analysis")
            raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"Error running pipeline: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def validate(
    config: str = typer.Option(..., "--config", "-c", help="Path to config YAML file"),
):
    """Validate a configuration file."""
    try:
        config_dict = load_config(config)
        typer.echo(f"✓ Config file is valid: {config}")
        typer.echo(f"  Keys: {list(config_dict.keys())}")

        # Try to create config objects to validate structure
        if "input_path" in config_dict:
            if "value_column" in config_dict:
                AMIAnomalyConfig(**config_dict)
                typer.echo("  Type: AMI Anomaly Config")
            elif "asset_id_column" in config_dict:
                AssetDegradationConfig(**config_dict)
                typer.echo("  Type: Asset Degradation Config")
            elif "consumption_column" in config_dict:
                LoadShapeConfig(**config_dict)
                typer.echo("  Type: Load Shape Config")
            else:
                OutageDetectionConfig(**config_dict)
                typer.echo("  Type: Outage Detection Config")

    except Exception as e:
        typer.echo(f"✗ Config file validation failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def info():
    """Display information about GridSmith."""
    typer.echo("GridSmith: Orchestration and reference app layer for ML4U chapter examples")
    typer.echo("")
    typer.echo("Available pipelines:")
    typer.echo("  - ami-anomaly: AMI anomaly detection")
    typer.echo("  - temperature-load: Temperature-to-load modeling (Chapter 1)")
    typer.echo("  - load-forecasting: Load forecasting (Chapter 4)")
    typer.echo("  - predictive-maintenance: Predictive maintenance (Chapter 5)")
    typer.echo("  - outage-prediction: Outage prediction (Chapter 6)")
    typer.echo("  - outage-detect: Outage event detection")
    typer.echo("  - asset-degradation: Asset degradation analysis")
    typer.echo("  - load-shape: Load shape analysis")
    typer.echo("")
    typer.echo("Usage:")
    typer.echo("  gridsmith run <pipeline> --config <config.yaml>")
    typer.echo("  gridsmith validate --config <config.yaml>")
    typer.echo("  gridsmith info")


if __name__ == "__main__":
    app()

