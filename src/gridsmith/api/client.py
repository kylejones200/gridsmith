"""Define GridSmithClient with methods that map to book chapters.

This module provides the stable public API for GridSmith.
"""

from pathlib import Path
from typing import Optional

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
from gridsmith.api.results import (
    AMIAnomalyResults,
    AssetDegradationResults,
    LoadForecastingResults,
    LoadShapeResults,
    OutageDetectionResults,
    OutagePredictionResults,
    PredictiveMaintenanceResults,
    TemperatureLoadResults,
)
from gridsmith.core.pipelines import (
    run_ami_anomaly_pipeline,
    run_load_forecasting_pipeline,
    run_outage_event_pipeline,
    run_outage_prediction_pipeline,
    run_predictive_maintenance_pipeline,
    run_temperature_load_pipeline,
    run_transformer_forecast_pipeline,
)


class GridSmithClient:
    """Client for running GridSmith chapter pipelines.

    This class provides a simple interface to run ML4U chapter examples.
    Each method corresponds to a chapter in the book.
    """

    def __init__(self):
        """Initialize the GridSmith client."""
        pass

    def ami_anomaly(self, config: AMIAnomalyConfig) -> AMIAnomalyResults:
        """Run AMI anomaly detection pipeline.

        Args:
            config: Configuration for AMI anomaly detection

        Returns:
            Results with metrics, tables, and figures
        """
        core_config = config.to_core_config()
        results = run_ami_anomaly_pipeline(core_config)

        return AMIAnomalyResults(
            metrics=results.metrics,
            output_dir=results.output_dir,
            tables=results.tables,
            figures=results.figures,
            metadata=results.metadata,
        )

    def outage_detection(self, config: OutageDetectionConfig) -> OutageDetectionResults:
        """Run outage event detection pipeline.

        Args:
            config: Configuration for outage detection

        Returns:
            Results with metrics, tables, and figures
        """
        core_config = config.to_core_config()
        results = run_outage_event_pipeline(core_config)

        return OutageDetectionResults(
            metrics=results.metrics,
            output_dir=results.output_dir,
            tables=results.tables,
            figures=results.figures,
            metadata=results.metadata,
        )

    def asset_degradation(self, config: AssetDegradationConfig) -> AssetDegradationResults:
        """Run asset degradation analysis pipeline.

        Args:
            config: Configuration for asset degradation analysis

        Returns:
            Results with metrics, tables, and figures
        """
        # TODO: Implement when pipeline is ready
        # For now, use outage pipeline as placeholder
        from gridsmith.core.pipelines import Config

        core_config = Config(
            input_path=config.input_path,
            output_dir=config.output_dir,
            dataset_spec=config.to_core_config().dataset_spec,
            metadata=config.metadata,
        )
        results = run_outage_event_pipeline(core_config)

        return AssetDegradationResults(
            metrics=results.metrics,
            output_dir=results.output_dir,
            tables=results.tables,
            figures=results.figures,
            metadata=results.metadata,
        )

    def load_shape(self, config: LoadShapeConfig) -> LoadShapeResults:
        """Run load shape analysis pipeline.

        Args:
            config: Configuration for load shape analysis

        Returns:
            Results with metrics, tables, and figures
        """
        # TODO: Implement when pipeline is ready
        # For now, use outage pipeline as placeholder
        from gridsmith.core.pipelines import Config

        core_config = Config(
            input_path=config.input_path,
            output_dir=config.output_dir,
            dataset_spec=config.to_core_config().dataset_spec,
            metadata=config.metadata,
        )
        results = run_outage_event_pipeline(core_config)

        return LoadShapeResults(
            metrics=results.metrics,
            output_dir=results.output_dir,
            tables=results.tables,
            figures=results.figures,
            metadata=results.metadata,
        )

    def temperature_load(self, config: TemperatureLoadConfig) -> TemperatureLoadResults:
        """Run temperature-to-load modeling pipeline.

        Args:
            config: Configuration for temperature-to-load modeling

        Returns:
            Results with metrics, tables, and figures
        """
        core_config = config.to_core_config()
        results = run_temperature_load_pipeline(core_config)

        return TemperatureLoadResults(
            metrics=results.metrics,
            output_dir=results.output_dir,
            tables=results.tables,
            figures=results.figures,
            metadata=results.metadata,
        )

    def load_forecasting(self, config: LoadForecastingConfig) -> LoadForecastingResults:
        """Run load forecasting pipeline.

        Args:
            config: Configuration for load forecasting

        Returns:
            Results with metrics, tables, and figures
        """
        core_config = config.to_core_config()
        results = run_load_forecasting_pipeline(core_config)

        return LoadForecastingResults(
            metrics=results.metrics,
            output_dir=results.output_dir,
            tables=results.tables,
            figures=results.figures,
            metadata=results.metadata,
        )

    def predictive_maintenance(self, config: PredictiveMaintenanceConfig) -> PredictiveMaintenanceResults:
        """Run predictive maintenance pipeline.

        Args:
            config: Configuration for predictive maintenance

        Returns:
            Results with metrics, tables, and figures
        """
        core_config = config.to_core_config()
        results = run_predictive_maintenance_pipeline(core_config)

        return PredictiveMaintenanceResults(
            metrics=results.metrics,
            output_dir=results.output_dir,
            tables=results.tables,
            figures=results.figures,
            metadata=results.metadata,
        )

    def outage_prediction(self, config: OutagePredictionConfig) -> OutagePredictionResults:
        """Run outage prediction pipeline.

        Args:
            config: Configuration for outage prediction

        Returns:
            Results with metrics, tables, and figures
        """
        core_config = config.to_core_config()
        results = run_outage_prediction_pipeline(core_config)

        return OutagePredictionResults(
            metrics=results.metrics,
            output_dir=results.output_dir,
            tables=results.tables,
            figures=results.figures,
            metadata=results.metadata,
        )

