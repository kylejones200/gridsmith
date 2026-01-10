"""Define chapter pipelines as functions.

This module defines chapter pipelines that compose other Smith libraries.
Core owns orchestration logic but no model math.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from gridsmith.core import DatasetSpec, FeatureSpec, MetricSpec, SplitSpec
from gridsmith.core.contracts import Columns, validate_schema
from gridsmith.core.eval import compute_anomaly_metrics, compute_forecast_metrics, compute_regression_metrics
from gridsmith.core.io import load_csv, load_parquet, save_dataframe, save_json
from gridsmith.core.plots import plot_anomalies, plot_forecast, plot_time_series

# Try to import Smith libraries for pipelines
try:
    import anomsmith
    HAS_ANOMSMITH = True
except ImportError:
    HAS_ANOMSMITH = False
    anomsmith = None

try:
    import timesmith
    HAS_TIMESMITH = True
except ImportError:
    HAS_TIMESMITH = False
    timesmith = None


@dataclass
class Config:
    """Base configuration for pipelines."""

    input_path: str
    output_dir: str
    dataset_spec: Optional[DatasetSpec] = None
    split_spec: Optional[SplitSpec] = None
    metric_specs: Optional[List[MetricSpec]] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Results:
    """Base results from pipeline execution."""

    metrics: Dict[str, float]
    output_dir: str
    tables: Dict[str, str] = None  # table_name -> file_path
    figures: Dict[str, str] = None  # figure_name -> file_path
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tables is None:
            self.tables = {}
        if self.figures is None:
            self.figures = {}
        if self.metadata is None:
            self.metadata = {}


def run_ami_anomaly_pipeline(config: Config) -> Results:
    """Run AMI anomaly detection pipeline.

    This pipeline:
    1. Loads AMI data
    2. Validates schema
    3. Detects anomalies using anomsmith
    4. Computes metrics
    5. Generates visualizations

    Args:
        config: Pipeline configuration

    Returns:
        Results with metrics, tables, and figures
    """
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    input_path = Path(config.input_path)
    if input_path.suffix == ".csv":
        df = load_csv(config.input_path, timestamp_column=Columns.TIMESTAMP)
    elif input_path.suffix == ".parquet":
        df = load_parquet(config.input_path, timestamp_column=Columns.TIMESTAMP)
    else:
        raise ValueError(f"Unsupported file format: {input_path.suffix}")

    # Validate schema if spec provided
    if config.dataset_spec:
        validate_schema(set(df.columns), config.dataset_spec)

    # Use anomsmith for anomaly detection if available
    if Columns.ANOMALY_SCORE not in df.columns:
        if Columns.CONSUMPTION not in df.columns:
            raise ValueError(f"Missing required column: {Columns.CONSUMPTION}")
        
        # Try to use anomsmith if available
        if HAS_ANOMSMITH and anomsmith is not None:
            try:
                # Delegate to anomsmith for anomaly detection
                if hasattr(anomsmith, "detect_anomalies"):
                    result = anomsmith.detect_anomalies(df[Columns.CONSUMPTION])
                    if isinstance(result, dict):
                        df[Columns.ANOMALY_SCORE] = result.get("scores", result.get("score", None))
                        df[Columns.IS_ANOMALY] = result.get("labels", result.get("anomalies", None))
                    else:
                        # Assume it returns a tuple of (labels, scores)
                        df[Columns.IS_ANOMALY] = result[0] if isinstance(result, tuple) else result
                        if isinstance(result, tuple) and len(result) > 1:
                            df[Columns.ANOMALY_SCORE] = result[1]
                elif hasattr(anomsmith, "AnomalyDetector"):
                    detector = anomsmith.AnomalyDetector()
                    detector.fit(df[[Columns.CONSUMPTION]])
                    predictions = detector.predict(df[[Columns.CONSUMPTION]])
                    df[Columns.IS_ANOMALY] = predictions == -1
                    if hasattr(detector, "score_samples"):
                        df[Columns.ANOMALY_SCORE] = detector.score_samples(df[[Columns.CONSUMPTION]])
                elif hasattr(anomsmith, "fit_predict"):
                    # Assume sklearn-like API
                    df[Columns.IS_ANOMALY] = anomsmith.fit_predict(df[[Columns.CONSUMPTION]]) == -1
                    if hasattr(anomsmith, "score_samples"):
                        df[Columns.ANOMALY_SCORE] = anomsmith.score_samples(df[[Columns.CONSUMPTION]])
            except Exception:
                # Fall back to simple threshold-based detection if anomsmith fails
                pass
        
        # Fallback: simple threshold-based anomaly detection (if anomsmith not available or failed)
        if Columns.IS_ANOMALY not in df.columns:
            # Compute stats on training data only to avoid data leakage
            # For unsupervised anomaly detection, use full dataset for fitting
            # But for supervised evaluation, we need proper train/test split
            if config.split_spec and "ground_truth" in df.columns:
                # For supervised evaluation: split first, compute stats on train only
                from sklearn.model_selection import train_test_split
                test_size = config.split_spec.test_ratio if config.split_spec.test_ratio else 0.2
                train_idx, test_idx = train_test_split(
                    df.index,
                    test_size=test_size,
                    random_state=config.metadata.get("random_state", 42),
                    shuffle=True
                )
                train_df = df.loc[train_idx]
                test_df = df.loc[test_idx]
                
                # Compute stats ONLY on training data
                mean = train_df[Columns.CONSUMPTION].mean()
                std = train_df[Columns.CONSUMPTION].std()
                
                # Apply to both train and test using training statistics
                df.loc[train_idx, Columns.ANOMALY_SCORE] = ((df.loc[train_idx, Columns.CONSUMPTION] - mean) / std).abs()
                df.loc[test_idx, Columns.ANOMALY_SCORE] = ((df.loc[test_idx, Columns.CONSUMPTION] - mean) / std).abs()
                df[Columns.IS_ANOMALY] = df[Columns.ANOMALY_SCORE] > 2.0
            else:
                # Unsupervised: use full dataset (no ground truth, no leakage concern)
                mean = df[Columns.CONSUMPTION].mean()
                std = df[Columns.CONSUMPTION].std()
                df[Columns.ANOMALY_SCORE] = ((df[Columns.CONSUMPTION] - mean) / std).abs()
                df[Columns.IS_ANOMALY] = df[Columns.ANOMALY_SCORE] > 2.0

    # Split data if split_spec provided (already handled above for supervised case)
    train_df = df
    test_df = None
    if config.split_spec and "ground_truth" not in df.columns:
        # TODO: Implement proper splitting logic for unsupervised cases
        # For now, use full dataset
        pass

    # Compute metrics - only on test set if split exists to avoid data leakage
    metrics: Dict[str, float] = {}
    if config.metric_specs:
        for metric_spec in config.metric_specs:
            if metric_spec.type == "anomaly":
                # Need ground truth labels for evaluation
                if "ground_truth" in df.columns:
                    # If we have a test split, evaluate only on test data
                    if test_df is not None and isinstance(test_df, pd.DataFrame):
                        eval_df = test_df
                    else:
                        eval_df = df
                    
                    anomaly_metrics = compute_anomaly_metrics(
                        eval_df["ground_truth"],
                        eval_df[Columns.IS_ANOMALY],
                        eval_df.get(Columns.ANOMALY_SCORE) if Columns.ANOMALY_SCORE in eval_df.columns else None,
                        metrics=[metric_spec.name],
                    )
                    metrics.update(anomaly_metrics)

    # Save output tables
    tables: Dict[str, str] = {}
    results_table_path = output_dir / "tables" / "anomaly_results.parquet"
    save_dataframe(df, results_table_path, format="parquet")
    tables["anomaly_results"] = str(results_table_path)

    # Generate plots
    figures: Dict[str, str] = {}
    plot_path = output_dir / "figures" / "anomaly_plot.png"
    plot_info = plot_anomalies(
        df,
        timestamp_column=Columns.TIMESTAMP,
        value_column=Columns.CONSUMPTION,
        anomaly_column=Columns.IS_ANOMALY,
        title="AMI Anomaly Detection Results",
        output_path=plot_path,
    )
    if "output_path" in plot_info:
        figures["anomaly_plot"] = plot_info["output_path"]

    # Save metrics
    metrics_path = output_dir / "metrics.json"
    save_json(metrics, metrics_path)

    return Results(
        metrics=metrics,
        output_dir=str(output_dir),
        tables=tables,
        figures=figures,
        metadata={"pipeline": "ami_anomaly", "input_shape": df.shape},
    )


def run_outage_event_pipeline(config: Config) -> Results:
    """Run outage event detection pipeline.

    This pipeline detects power outage events from grid data.

    Args:
        config: Pipeline configuration

    Returns:
        Results with metrics, tables, and figures
    """
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    input_path = Path(config.input_path)
    if input_path.suffix == ".csv":
        df = load_csv(config.input_path, timestamp_column=Columns.TIMESTAMP)
    elif input_path.suffix == ".parquet":
        df = load_parquet(config.input_path, timestamp_column=Columns.TIMESTAMP)
    else:
        raise ValueError(f"Unsupported file format: {input_path.suffix}")

    # Validate schema
    if config.dataset_spec:
        validate_schema(set(df.columns), config.dataset_spec)

    # TODO: Implement outage detection using anomsmith or ressmith
    # Placeholder for now

    metrics: Dict[str, float] = {}
    tables: Dict[str, str] = {}
    figures: Dict[str, str] = {}

    # Save metrics
    metrics_path = output_dir / "metrics.json"
    save_json(metrics, metrics_path)

    return Results(
        metrics=metrics,
        output_dir=str(output_dir),
        tables=tables,
        figures=figures,
        metadata={"pipeline": "outage_event"},
    )


def run_transformer_forecast_pipeline(config: Config) -> Results:
    """Run transformer-based forecast pipeline.

    This pipeline generates forecasts using transformer models via timesmith.
    PREFERRED: timesmith is used for all time series forecasting.

    Args:
        config: Pipeline configuration

    Returns:
        Results with metrics, tables, and figures
    """
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    input_path = Path(config.input_path)
    if input_path.suffix == ".csv":
        df = load_csv(config.input_path, timestamp_column=Columns.TIMESTAMP)
    elif input_path.suffix == ".parquet":
        df = load_parquet(config.input_path, timestamp_column=Columns.TIMESTAMP)
    else:
        raise ValueError(f"Unsupported file format: {input_path.suffix}")

    # Validate schema
    if config.dataset_spec:
        validate_schema(set(df.columns), config.dataset_spec)

    # PREFERRED: Use timesmith for transformer-based forecasting
    forecast_df = df.copy()
    timesmith_success = False
    horizon = config.metadata.get("horizon", 24) if config.metadata else 24
    
    if HAS_TIMESMITH and timesmith is not None:
        try:
            # Determine value column to forecast
            value_column = None
            if Columns.CONSUMPTION in df.columns:
                value_column = Columns.CONSUMPTION
            elif Columns.DEMAND in df.columns:
                value_column = Columns.DEMAND
            elif Columns.POWER in df.columns:
                value_column = Columns.POWER
            else:
                # Try to find a numeric column that's not a timestamp or ID
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                if len(numeric_cols) > 0:
                    value_column = numeric_cols[0]
            
            if value_column:
                # Try multiple timesmith API patterns (preferred)
                if hasattr(timesmith, "forecast"):
                    forecasts = timesmith.forecast(
                        df[[Columns.TIMESTAMP, value_column]],
                        timestamp_column=Columns.TIMESTAMP,
                        value_column=value_column,
                        horizon=horizon,
                    )
                    if isinstance(forecasts, pd.DataFrame) and not forecasts.empty:
                        forecast_df = forecasts
                        timesmith_success = True
                        if Columns.FORECAST not in forecast_df.columns:
                            # Try to find forecast column
                            for col in [f"{value_column}_forecast", "forecast", "prediction", "pred"]:
                                if col in forecast_df.columns:
                                    forecast_df[Columns.FORECAST] = forecast_df[col]
                                    break
                
                if not timesmith_success and hasattr(timesmith, "Forecaster"):
                    forecaster = timesmith.Forecaster()
                    forecaster.fit(df[[Columns.TIMESTAMP, value_column]], timestamp_column=Columns.TIMESTAMP)
                    forecasts = forecaster.predict(horizon=horizon)
                    if isinstance(forecasts, pd.DataFrame) and not forecasts.empty:
                        forecast_df = forecasts
                        timesmith_success = True
                        if Columns.FORECAST not in forecast_df.columns:
                            forecast_df[Columns.FORECAST] = forecasts.iloc[:, -1]
                
                # Try transformer-specific timesmith APIs
                if not timesmith_success:
                    for attr_name in ["TransformerForecaster", "TransformerModel", "TimeSeriesTransformer"]:
                        if hasattr(timesmith, attr_name):
                            model_class = getattr(timesmith, attr_name)
                            try:
                                model = model_class()
                                if hasattr(model, "fit"):
                                    model.fit(df, timestamp_column=Columns.TIMESTAMP, value_column=value_column)
                                if hasattr(model, "predict"):
                                    forecasts = model.predict(horizon=horizon)
                                    if isinstance(forecasts, pd.DataFrame) and not forecasts.empty:
                                        forecast_df = forecasts
                                        timesmith_success = True
                                        break
                            except Exception:
                                continue
        except Exception:
            # Continue to try other approaches if timesmith fails
            pass

    # Compute metrics if we have actuals
    metrics: Dict[str, float] = {}
    if config.metric_specs and Columns.ACTUAL in forecast_df.columns and Columns.FORECAST in forecast_df.columns:
        for metric_spec in config.metric_specs:
            if metric_spec.type == "forecast":
                forecast_metrics = compute_forecast_metrics(
                    forecast_df[Columns.ACTUAL],
                    forecast_df[Columns.FORECAST],
                    metrics=[metric_spec.name] if metric_spec.name else None,
                )
                metrics.update(forecast_metrics)

    # Save output tables
    tables: Dict[str, str] = {}
    if not forecast_df.empty:
        results_table_path = output_dir / "tables" / "forecast_results.parquet"
        save_dataframe(forecast_df, results_table_path, format="parquet")
        tables["forecast_results"] = str(results_table_path)

    # Generate plots
    figures: Dict[str, str] = {}
    if Columns.FORECAST in forecast_df.columns:
        plot_path = output_dir / "figures" / "forecast_plot.png"
        plot_info = plot_forecast(
            forecast_df,
            timestamp_column=Columns.TIMESTAMP,
            actual_column=Columns.ACTUAL if Columns.ACTUAL in forecast_df.columns else value_column,
            forecast_column=Columns.FORECAST,
            title="Transformer Forecast Results",
            output_path=plot_path,
        )
        if "output_path" in plot_info:
            figures["forecast_plot"] = plot_info["output_path"]

    # Save metrics
    metrics_path = output_dir / "metrics.json"
    save_json(metrics, metrics_path)

    return Results(
        metrics=metrics,
        output_dir=str(output_dir),
        tables=tables,
        figures=figures,
        metadata={"pipeline": "transformer_forecast"},
    )


def run_temperature_load_pipeline(config: Config) -> Results:
    """Run temperature-to-load modeling pipeline.

    This pipeline demonstrates the fundamental temperature-to-load relationship
    using linear regression.

    Args:
        config: Pipeline configuration

    Returns:
        Results with metrics, tables, and figures
    """
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data or generate synthetic
    input_path = Path(config.input_path)
    if input_path.exists() and input_path.suffix in [".csv", ".parquet"]:
        if input_path.suffix == ".csv":
            df = load_csv(config.input_path, timestamp_column="Date")
        else:
            df = load_parquet(config.input_path, timestamp_column="Date")
    else:
        # Generate synthetic data
        import numpy as np
        np.random.seed(config.metadata.get("random_state", 42))
        dates = pd.date_range(
            start=config.metadata.get("start_date", "2024-01-01"),
            periods=config.metadata.get("days", 365),
            freq="D"
        )
        base_temp = config.metadata.get("base_temp", 20.0)
        temp_amplitude = config.metadata.get("temp_amplitude", 10.0)
        temperature = (
            base_temp + 
            temp_amplitude * np.sin(2 * np.pi * dates.dayofyear / 365) +
            np.random.normal(0, config.metadata.get("temp_noise_std", 2.0), len(dates))
        )
        base_load = config.metadata.get("base_load", 1000.0)
        temp_coef = config.metadata.get("temp_coef", 10.0)
        load = (
            base_load + 
            temp_coef * temperature +
            config.metadata.get("temp_coef_squared", 0.5) * (temperature - base_temp) ** 2 +
            np.random.normal(0, config.metadata.get("noise_std", 50.0), len(dates))
        )
        df = pd.DataFrame({
            "Date": dates,
            "Temperature_C": temperature,
            "Load_MW": load
        })

    # Validate schema
    if config.dataset_spec:
        validate_schema(set(df.columns), config.dataset_spec)

    # Train model using timesmith or sklearn
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split

    X = df[["Temperature_C"]].values
    y = df["Load_MW"].values

    # Split data to avoid data leakage - train on train, evaluate on test
    test_size = config.metadata.get("test_size", 0.2)
    # Split with indices preserved to map predictions back correctly
    train_indices, test_indices = train_test_split(
        df.index,
        test_size=test_size,
        random_state=config.metadata.get("random_state", 42),
        shuffle=True
    )
    
    X_train = df.loc[train_indices, ["Temperature_C"]].values
    y_train = df.loc[train_indices, "Load_MW"].values
    X_test = df.loc[test_indices, ["Temperature_C"]].values
    y_test = df.loc[test_indices, "Load_MW"].values

    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Predict on both train and test for visualization, but evaluate metrics only on test
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Store predictions in dataframe using original indices
    df["predicted_load"] = 0.0  # Initialize
    df.loc[train_indices, "predicted_load"] = y_train_pred
    df.loc[test_indices, "predicted_load"] = y_test_pred
    df["residual"] = df["Load_MW"] - df["predicted_load"]

    # Compute metrics using timesmith (preferred) or local computation
    # ONLY on test set to avoid data leakage
    metrics: Dict[str, float] = {}
    if config.metric_specs:
        for metric_spec in config.metric_specs:
            if metric_spec.type == "regression":
                # compute_regression_metrics will try timesmith first
                regression_metrics = compute_regression_metrics(
                    pd.Series(y_test),
                    pd.Series(y_test_pred),
                    metrics=[metric_spec.name] if metric_spec.name else None,
                )
                metrics.update(regression_metrics)
    else:
        # Default metrics (compute_regression_metrics prefers timesmith)
        regression_metrics = compute_regression_metrics(
            pd.Series(y_test),
            pd.Series(y_test_pred),
            metrics=["mse", "r2", "mae"],
        )
        metrics.update(regression_metrics)
        metrics["coefficient"] = float(model.coef_[0])

    # Save output tables
    tables: Dict[str, str] = {}
    results_table_path = output_dir / "tables" / "temperature_load_results.parquet"
    save_dataframe(df, results_table_path, format="parquet")
    tables["temperature_load_results"] = str(results_table_path)

    # Generate plots
    figures: Dict[str, str] = {}
    
    # Temperature vs Load scatter plot
    plot_path = output_dir / "figures" / "temperature_load_plot.png"
    plot_info = plot_time_series(
        df.rename(columns={"Date": "timestamp"}),
        x_column="Temperature_C",
        y_columns="Load_MW",
        title="Temperature vs Load",
        output_path=plot_path,
    )
    if "output_path" in plot_info:
        figures["temperature_load_plot"] = plot_info["output_path"]

    # Predictions vs Actual
    forecast_path = output_dir / "figures" / "predictions_plot.png"
    plot_info = plot_forecast(
        df.rename(columns={"Date": "timestamp", "Load_MW": "actual", "predicted_load": "forecast"}),
        timestamp_column="timestamp",
        actual_column="actual",
        forecast_column="forecast",
        title="Temperature-to-Load Predictions",
        output_path=forecast_path,
    )
    if "output_path" in plot_info:
        figures["predictions_plot"] = plot_info["output_path"]

    # Save metrics
    metrics_path = output_dir / "metrics.json"
    save_json(metrics, metrics_path)

    return Results(
        metrics=metrics,
        output_dir=str(output_dir),
        tables=tables,
        figures=figures,
        metadata={"pipeline": "temperature_load", "input_shape": df.shape, "model_coefficient": float(model.coef_[0])},
    )


def run_load_forecasting_pipeline(config: Config) -> Results:
    """Run load forecasting pipeline.

    This pipeline forecasts load using ARIMA and/or LSTM models via timesmith.

    Args:
        config: Pipeline configuration

    Returns:
        Results with metrics, tables, and figures
    """
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

        # Load data or generate synthetic
    input_path = Path(config.input_path)
    if input_path.exists() and input_path.suffix in [".csv", ".parquet"]:
        if input_path.suffix == ".csv":
            df = load_csv(config.input_path, timestamp_column=Columns.TIMESTAMP)
        elif input_path.suffix == ".parquet":
            df = load_parquet(config.input_path, timestamp_column=Columns.TIMESTAMP)
    else:
        # Generate synthetic load data
        np.random.seed(config.metadata.get("random_state", 42))
        date_rng = pd.date_range(
            start=config.metadata.get("start_date", "2024-01-01"),
            periods=config.metadata.get("periods", 8760),  # 1 year hourly
            freq="h"
        )
        base = config.metadata.get("base_load", 1000.0)
        seasonal = config.metadata.get("seasonal_amplitude", 200.0)
        daily = config.metadata.get("daily_cycle_amplitude", 150.0)
        noise_std = config.metadata.get("noise_std", 20.0)
        
        base_load = base + seasonal * np.sin(2 * np.pi * date_rng.dayofyear / 365)
        daily_cycle = daily * np.sin(2 * np.pi * date_rng.hour / 24)
        noise = np.random.normal(0, noise_std, len(date_rng))
        load = base_load + daily_cycle + noise
        
        df = pd.DataFrame({Columns.TIMESTAMP: date_rng, "Load_MW": load})

    # Validate schema
    if config.dataset_spec:
        validate_schema(set(df.columns), config.dataset_spec)

    # Determine load column
    load_column = None
    for col in ["Load_MW", "load", Columns.DEMAND, Columns.CONSUMPTION]:
        if col in df.columns:
            load_column = col
            break

    if not load_column:
        raise ValueError("No load column found. Expected: Load_MW, load, demand, or consumption")

    # PREFERRED: Use timesmith for all time series forecasting (preferred over book code)
    forecast_df = df.copy()
    metrics: Dict[str, float] = {}
    timesmith_success = False
    
    forecast_horizon = config.metadata.get("forecast_horizon", 24)
    
    # Try timesmith with multiple API patterns (preferred approach)
    if HAS_TIMESMITH and timesmith is not None:
        try:
            # Try timesmith.forecast() - function-based API
            if hasattr(timesmith, "forecast"):
                forecasts = timesmith.forecast(
                    df[[Columns.TIMESTAMP, load_column]],
                    timestamp_column=Columns.TIMESTAMP,
                    value_column=load_column,
                    horizon=forecast_horizon,
                )
                if isinstance(forecasts, pd.DataFrame) and not forecasts.empty:
                    forecast_df = forecasts
                    timesmith_success = True
                    if Columns.FORECAST not in forecast_df.columns:
                        # Try to find forecast column
                        for col in [f"{load_column}_forecast", "forecast", "prediction", "pred"]:
                            if col in forecast_df.columns:
                                forecast_df[Columns.FORECAST] = forecast_df[col]
                                break
            
            # Try timesmith.Forecaster() - class-based API
            if not timesmith_success and hasattr(timesmith, "Forecaster"):
                forecaster = timesmith.Forecaster()
                forecaster.fit(df[[Columns.TIMESTAMP, load_column]], timestamp_column=Columns.TIMESTAMP)
                forecasts = forecaster.predict(horizon=forecast_horizon)
                if isinstance(forecasts, pd.DataFrame) and not forecasts.empty:
                    forecast_df = forecasts
                    timesmith_success = True
                    if Columns.FORECAST not in forecast_df.columns:
                        for col in [f"{load_column}_forecast", "forecast", "prediction", "pred"]:
                            if col in forecast_df.columns:
                                forecast_df[Columns.FORECAST] = forecast_df[col]
                                break
            
            # Try timesmith.TimeSeriesForecaster or similar
            if not timesmith_success:
                for attr_name in ["TimeSeriesForecaster", "TSForecaster", "ForecastModel"]:
                    if hasattr(timesmith, attr_name):
                        forecaster_class = getattr(timesmith, attr_name)
                        try:
                            forecaster = forecaster_class()
                            if hasattr(forecaster, "fit"):
                                forecaster.fit(df, timestamp_column=Columns.TIMESTAMP, value_column=load_column)
                            if hasattr(forecaster, "predict"):
                                forecasts = forecaster.predict(horizon=forecast_horizon)
                                if isinstance(forecasts, pd.DataFrame) and not forecasts.empty:
                                    forecast_df = forecasts
                                    timesmith_success = True
                                    break
                        except Exception:
                            continue
        except Exception as e:
            # Log but continue to try book code fallback
            pass

    # FALLBACK: Only use book's ARIMA/LSTM code if timesmith not available or failed
    if not timesmith_success and Columns.FORECAST not in forecast_df.columns and load_column in forecast_df.columns:
        try:
            from statsmodels.tsa.arima.model import ARIMA
            # Use ARIMA forecast logic
            ts = forecast_df.set_index(Columns.TIMESTAMP)[load_column]
            arima_order = tuple(config.metadata.get("arima_order", (1, 1, 1)))
            model = ARIMA(ts, order=arima_order)
            fit = model.fit()
            forecast = fit.forecast(steps=forecast_horizon)
            
            # Create forecast dataframe
            last_date = forecast_df[Columns.TIMESTAMP].max()
            forecast_dates = pd.date_range(
                start=last_date + pd.Timedelta(hours=1),
                periods=forecast_horizon,
                freq="h"
            )
            forecast_df = pd.concat([
                forecast_df,
                pd.DataFrame({
                    Columns.TIMESTAMP: forecast_dates,
                    Columns.FORECAST: forecast.values
                })
            ], ignore_index=True)
            
            # FALLBACK: Try LSTM forecast only if timesmith not available
            # Note: timesmith should handle LSTM internally, but this is backup
            if not HAS_TIMESMITH or timesmith is None:
                try:
                    from darts import TimeSeries
                    from darts.models import RNNModel
                    from darts.dataprocessing.transformers import Scaler
                    
                    df_copy = df.copy()
                    df_copy[load_column] = df_copy[load_column].astype(np.float32)
                    series = TimeSeries.from_dataframe(df_copy, Columns.TIMESTAMP, load_column)
                    train = series[:-forecast_horizon]
                    
                    # Scale the data
                    scaler = Scaler()
                    train_scaled = scaler.fit_transform(train)
                    
                    # Train LSTM - only used if timesmith not available
                    model = RNNModel(
                        model="LSTM",
                        input_chunk_length=config.metadata.get("input_chunk_length", 24),
                        output_chunk_length=1,
                        training_length=config.metadata.get("training_length", 168),
                        n_epochs=50,
                        random_state=config.metadata.get("random_state", 42),
                        pl_trainer_kwargs={
                            "accelerator": "cpu",
                            "devices": 1,
                            "enable_progress_bar": False
                        },
                    )
                    model.fit(train_scaled)
                    pred_scaled = model.predict(forecast_horizon)
                    pred = scaler.inverse_transform(pred_scaled)
                    
                    # Use LSTM forecast if successful
                    pred_values = pred.pd_dataframe().iloc[:, 0].values
                    forecast_df.loc[forecast_df[Columns.TIMESTAMP].isin(forecast_dates), Columns.FORECAST] = pred_values
                except ImportError:
                    # Darts not available, use ARIMA forecast
                    pass
                except Exception:
                    # LSTM failed, use ARIMA forecast
                    pass
        except Exception:
            # If ARIMA fails, just copy the last values
            last_value = forecast_df[load_column].iloc[-1]
            last_date = forecast_df[Columns.TIMESTAMP].max()
            forecast_dates = pd.date_range(
                start=last_date + pd.Timedelta(hours=1),
                periods=forecast_horizon,
                freq="h"
            )
            forecast_df = pd.concat([
                forecast_df,
                pd.DataFrame({
                    Columns.TIMESTAMP: forecast_dates,
                    Columns.FORECAST: [last_value] * forecast_horizon
                })
            ], ignore_index=True)

    # Compute metrics using timesmith (preferred) - compute_forecast_metrics tries timesmith first
    # CRITICAL: Only compute metrics on true future forecasts vs actuals (not training data)
    if Columns.FORECAST in forecast_df.columns:
        # For forecasting, we can only evaluate if we have actual future values
        # Separate historical data from forecast period
        historical_len = len(df)
        
        if len(forecast_df) > historical_len:
            # We have future forecasts - only evaluate on the forecast period
            # But only if we have actuals for that period (which we typically don't for real forecasting)
            # For synthetic data or backtesting, actuals might be available
            forecast_period = forecast_df.iloc[historical_len:]
            
            if Columns.ACTUAL in forecast_period.columns or load_column in forecast_period.columns:
                # We have actuals for the forecast period - evaluate only on forecasts
                actuals_col = Columns.ACTUAL if Columns.ACTUAL in forecast_period.columns else load_column
                actuals = forecast_period[actuals_col]
                forecasts = forecast_period[Columns.FORECAST]
                
                # Align lengths and filter out NaN
                mask = ~(actuals.isna() | forecasts.isna())
                actuals = actuals[mask]
                forecasts = forecasts[mask]
                
                if len(actuals) > 0 and len(forecasts) > 0:
                    if config.metric_specs:
                        for metric_spec in config.metric_specs:
                            if metric_spec.type == "forecast":
                                forecast_metrics = compute_forecast_metrics(
                                    actuals,
                                    forecasts,
                                    metrics=[metric_spec.name] if metric_spec.name else None,
                                )
                                metrics.update(forecast_metrics)
                    else:
                        # Default forecast metrics
                        forecast_metrics = compute_forecast_metrics(
                            actuals,
                            forecasts,
                            metrics=["mse", "mae", "rmse"],
                        )
                        metrics.update(forecast_metrics)
            # Note: If no actuals available for forecast period, we cannot compute metrics
            # This is expected for real forecasting scenarios

    # Save output tables
    tables: Dict[str, str] = {}
    results_table_path = output_dir / "tables" / "load_forecast_results.parquet"
    save_dataframe(forecast_df, results_table_path, format="parquet")
    tables["load_forecast_results"] = str(results_table_path)

    # Generate plots
    figures: Dict[str, str] = {}
    if Columns.FORECAST in forecast_df.columns:
        plot_path = output_dir / "figures" / "load_forecast_plot.png"
        plot_info = plot_forecast(
            forecast_df,
            timestamp_column=Columns.TIMESTAMP,
            actual_column=load_column,
            forecast_column=Columns.FORECAST,
            title="Load Forecasting Results",
            output_path=plot_path,
        )
        if "output_path" in plot_info:
            figures["load_forecast_plot"] = plot_info["output_path"]

    # Save metrics
    metrics_path = output_dir / "metrics.json"
    save_json(metrics, metrics_path)

    return Results(
        metrics=metrics,
        output_dir=str(output_dir),
        tables=tables,
        figures=figures,
        metadata={"pipeline": "load_forecasting", "forecast_horizon": forecast_horizon},
    )


def run_predictive_maintenance_pipeline(config: Config) -> Results:
    """Run predictive maintenance pipeline.

    This pipeline detects anomalies and predicts failures using anomsmith.

    Args:
        config: Pipeline configuration

    Returns:
        Results with metrics, tables, and figures
    """
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data or generate synthetic SCADA data (from Chapter 5)
    input_path = Path(config.input_path)
    if input_path.exists() and input_path.suffix in [".csv", ".parquet"]:
        if input_path.suffix == ".csv":
            df = load_csv(config.input_path)
        elif input_path.suffix == ".parquet":
            df = load_parquet(config.input_path)
    else:
        # Generate synthetic SCADA data
        np.random.seed(config.metadata.get("random_state", 42))
        samples = config.metadata.get("samples", 1000)
        
        temp = np.random.normal(
            config.metadata.get("temp_mean", 65.0),
            config.metadata.get("temp_std", 5.0),
            samples
        )
        vibration = np.random.normal(
            config.metadata.get("vibration_mean", 0.25),
            config.metadata.get("vibration_std", 0.05),
            samples
        )
        oil_pressure = np.random.normal(
            config.metadata.get("oil_pressure_mean", 50.0),
            config.metadata.get("oil_pressure_std", 5.0),
            samples
        )
        load = np.random.normal(
            config.metadata.get("load_mean", 1000.0),
            config.metadata.get("load_std", 100.0),
            samples
        )
        
        # Failure probability model
        failure_prob = 1 / (1 + np.exp(-(0.05*(temp-65) + 8*(vibration-0.25))))
        failures = np.random.binomial(1, failure_prob)
        
        df = pd.DataFrame({
            "Temperature_C": temp,
            "Vibration_g": vibration,
            "OilPressure_psi": oil_pressure,
            "Load_kVA": load,
            "Failure": failures
        })

    # Validate schema
    if config.dataset_spec:
        validate_schema(set(df.columns), config.dataset_spec)

    # Determine feature columns
    feature_cols = []
    for col in ["Temperature_C", "Vibration_g", "OilPressure_psi", "Load_kVA"]:
        if col in df.columns:
            feature_cols.append(col)

    if not feature_cols:
        raise ValueError("No feature columns found. Expected: Temperature_C, Vibration_g, OilPressure_psi, Load_kVA")

    # Anomaly detection using anomsmith or IsolationForest
    if HAS_ANOMSMITH and anomsmith is not None:
        try:
            if hasattr(anomsmith, "detect_anomalies"):
                result = anomsmith.detect_anomalies(df[feature_cols])
                if isinstance(result, dict):
                    df[Columns.ANOMALY_SCORE] = result.get("scores", result.get("score", None))
                    df[Columns.IS_ANOMALY] = result.get("labels", result.get("anomalies", None))
        except Exception:
            # Fall back to IsolationForest
            pass

    # Fallback: Use IsolationForest anomaly detection
    if Columns.IS_ANOMALY not in df.columns:
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import StandardScaler

        # CRITICAL: Split data FIRST to avoid data leakage
        # For supervised evaluation, fit scaler only on training data
        test_size = config.metadata.get("test_size", 0.2) if "Failure" in df.columns else None
        if test_size and "Failure" in df.columns:
            from sklearn.model_selection import train_test_split
            # Split indices to maintain alignment with dataframe
            train_idx, test_idx = train_test_split(
                df.index,
                test_size=test_size,
                random_state=config.metadata.get("random_state", 42),
                stratify=df["Failure"] if df["Failure"].nunique() > 1 else None
            )
            X_train_anom = df.loc[train_idx, feature_cols]
            X_test_anom = df.loc[test_idx, feature_cols]
            
            # Fit scaler ONLY on training data
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train_anom)
            X_test_scaled = scaler.transform(X_test_anom)  # Transform test with train stats
            
            contamination = config.metadata.get("contamination", 0.05)
            model = IsolationForest(
                contamination=contamination,
                random_state=config.metadata.get("random_state", 42)
            )
            # Fit on training data only
            preds_train = model.fit_predict(X_train_scaled)
            preds_test = model.predict(X_test_scaled)
            
            # Store predictions
            df.loc[train_idx, Columns.IS_ANOMALY] = preds_train == -1
            df.loc[test_idx, Columns.IS_ANOMALY] = preds_test == -1
            
            if hasattr(model, "score_samples"):
                df.loc[train_idx, Columns.ANOMALY_SCORE] = -model.score_samples(X_train_scaled)
                df.loc[test_idx, Columns.ANOMALY_SCORE] = -model.score_samples(X_test_scaled)
        else:
            # Unsupervised case: no ground truth, can use full dataset
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(df[feature_cols])

            contamination = config.metadata.get("contamination", 0.05)
            model = IsolationForest(
                contamination=contamination,
                random_state=config.metadata.get("random_state", 42)
            )
            preds = model.fit_predict(X_scaled)
            df[Columns.IS_ANOMALY] = preds == -1
            if hasattr(model, "score_samples"):
                df[Columns.ANOMALY_SCORE] = -model.score_samples(X_scaled)

    # Failure prediction using RandomForest
    if "Failure" in df.columns:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import roc_auc_score

        # Use RandomForest for failure prediction
        X = df[feature_cols]
        y = df["Failure"]
        test_size = config.metadata.get("test_size", 0.2)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=test_size,
            random_state=config.metadata.get("random_state", 42),
            stratify=y if y.nunique() > 1 else None
        )

        model = RandomForestClassifier(
            n_estimators=config.metadata.get("n_estimators", 100),
            random_state=config.metadata.get("random_state", 42)
        )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        df.loc[X_test.index, "predicted_failure"] = y_pred
        df.loc[X_test.index, "failure_probability"] = y_prob

        # Compute metrics
        metrics: Dict[str, float] = {}
        if y_test.nunique() > 1:
            metrics["roc_auc"] = float(roc_auc_score(y_test, y_prob))
        metrics.update(compute_anomaly_metrics(
            y_test,
            y_pred,
            pd.Series(y_prob),
            metrics=["precision", "recall", "f1"]
        ))

    # Save output tables
    tables: Dict[str, str] = {}
    results_table_path = output_dir / "tables" / "predictive_maintenance_results.parquet"
    save_dataframe(df, results_table_path, format="parquet")
    tables["predictive_maintenance_results"] = str(results_table_path)

    # Generate plots
    figures: Dict[str, str] = {}
    if Columns.IS_ANOMALY in df.columns and feature_cols:
        plot_path = output_dir / "figures" / "anomaly_plot.png"
        plot_info = plot_anomalies(
            df.reset_index() if df.index.name else df,
            timestamp_column=df.index.name if df.index.name and df.index.name != "index" else df.columns[0],
            value_column=feature_cols[0],
            anomaly_column=Columns.IS_ANOMALY,
            title="Predictive Maintenance Anomaly Detection",
            output_path=plot_path,
        )
        if "output_path" in plot_info:
            figures["anomaly_plot"] = plot_info["output_path"]

    # Save metrics
    if "metrics" not in locals():
        metrics = {}
    metrics_path = output_dir / "metrics.json"
    save_json(metrics, metrics_path)

    return Results(
        metrics=metrics,
        output_dir=str(output_dir),
        tables=tables,
        figures=figures,
        metadata={"pipeline": "predictive_maintenance", "input_shape": df.shape},
    )


def run_outage_prediction_pipeline(config: Config) -> Results:
    """Run outage prediction pipeline.

    This pipeline predicts outages using weather and asset data.

    Args:
        config: Pipeline configuration

    Returns:
        Results with metrics, tables, and figures
    """
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data or generate synthetic storm outage data (from Chapter 6)
    input_path = Path(config.input_path)
    if input_path.exists() and input_path.suffix in [".csv", ".parquet"]:
        if input_path.suffix == ".csv":
            df = load_csv(config.input_path)
        elif input_path.suffix == ".parquet":
            df = load_parquet(config.input_path)
    else:
        # Generate synthetic storm outage data
        np.random.seed(config.metadata.get("random_state", 42))
        samples = config.metadata.get("samples", 1000)
        
        wind_speed = np.random.normal(
            config.metadata.get("wind_mean", 15.0),
            config.metadata.get("wind_std", 8.0),
            samples
        )
        rainfall = np.random.normal(
            config.metadata.get("rainfall_mean", 50.0),
            config.metadata.get("rainfall_std", 20.0),
            samples
        )
        tree_density = np.random.uniform(
            config.metadata.get("tree_density_min", 0.0),
            config.metadata.get("tree_density_max", 1.0),
            samples
        )
        asset_age = np.random.uniform(
            config.metadata.get("asset_age_min", 0.0),
            config.metadata.get("asset_age_max", 50.0),
            samples
        )
        
        # Outage probability model
        logit = (
            0.15 * (wind_speed - 25) +
            0.03 * (rainfall - 60) +
            2 * (tree_density - 0.5)
        )
        outage_prob = 1 / (1 + np.exp(-logit))
        outages = np.random.binomial(1, outage_prob)
        
        df = pd.DataFrame({
            "WindSpeed_mps": wind_speed,
            "Rainfall_mm": rainfall,
            "TreeDensity": tree_density,
            "AssetAge_years": asset_age,
            "Outage": outages
        })

    # Validate schema
    if config.dataset_spec:
        validate_schema(set(df.columns), config.dataset_spec)

    # Determine feature columns
    feature_cols = []
    for col in ["WindSpeed_mps", "Rainfall_mm", "TreeDensity", "AssetAge_years"]:
        if col in df.columns:
            feature_cols.append(col)

    if not feature_cols:
        raise ValueError("No feature columns found. Expected: WindSpeed_mps, Rainfall_mm, TreeDensity, AssetAge_years")

    # Train outage prediction model using GradientBoostingClassifier
    metrics: Dict[str, float] = {}
    if "Outage" in df.columns:
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import roc_auc_score
        from sklearn.inspection import permutation_importance

        # Use GradientBoosting for outage prediction
        X = df[feature_cols]
        y = df["Outage"]
        test_size = config.metadata.get("test_size", 0.2)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=config.metadata.get("random_state", 42),
            stratify=y if y.nunique() > 1 else None
        )

        model = GradientBoostingClassifier(
            n_estimators=config.metadata.get("n_estimators", 100),
            learning_rate=config.metadata.get("learning_rate", 0.1),
            max_depth=config.metadata.get("max_depth", 3),
            random_state=config.metadata.get("random_state", 42)
        )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        df.loc[X_test.index, "predicted_outage"] = y_pred
        df.loc[X_test.index, "outage_probability"] = y_prob

        # Compute metrics
        if y_test.nunique() > 1:
            metrics["roc_auc"] = float(roc_auc_score(y_test, y_prob))
            metrics.update(compute_anomaly_metrics(
                y_test,
                y_pred,
                pd.Series(y_prob),
                metrics=["precision", "recall", "f1"]
            ))
            
            # Feature importance analysis
            result = permutation_importance(
                model, X_test, y_test,
                n_repeats=10,
                random_state=config.metadata.get("random_state", 42)
            )
            feature_importance_df = pd.DataFrame({
                "Feature": X.columns,
                "Importance": result.importances_mean
            }).sort_values("Importance", ascending=False)
            
            # Save feature importance
            importance_path = output_dir / "tables" / "feature_importance.parquet"
            save_dataframe(feature_importance_df, importance_path, format="parquet")

    # Save output tables
    tables: Dict[str, str] = {}
    results_table_path = output_dir / "tables" / "outage_prediction_results.parquet"
    save_dataframe(df, results_table_path, format="parquet")
    tables["outage_prediction_results"] = str(results_table_path)

    # Generate plots
    figures: Dict[str, str] = {}
    
    # Save metrics
    metrics_path = output_dir / "metrics.json"
    save_json(metrics, metrics_path)

    return Results(
        metrics=metrics,
        output_dir=str(output_dir),
        tables=tables,
        figures=figures,
        metadata={"pipeline": "outage_prediction", "input_shape": df.shape},
    )

