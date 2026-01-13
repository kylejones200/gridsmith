"""Define chapter pipelines as functions.

This module defines chapter pipelines that compose other Smith libraries.
Core owns orchestration logic but no model math.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd

from gridsmith.core import DatasetSpec, MetricSpec, SplitSpec
from gridsmith.core.contracts import Columns, validate_schema
from gridsmith.core.eval import (
    compute_anomaly_metrics,
    compute_forecast_metrics,
    compute_regression_metrics,
)
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
        self.metadata = self.metadata or {}


@dataclass
class Results:
    """Base results from pipeline execution."""

    metrics: Dict[str, float]
    output_dir: str
    tables: Dict[str, str] = None  # table_name -> file_path
    figures: Dict[str, str] = None  # figure_name -> file_path
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        self.tables = self.tables or {}
        self.figures = self.figures or {}
        self.metadata = self.metadata or {}


# Helper functions with dictionary dispatch and vectorized operations

LOADERS: Dict[str, Callable] = {
    ".csv": lambda path, **kwargs: load_csv(str(path), **kwargs),
    ".parquet": lambda path, **kwargs: load_parquet(str(path), **kwargs),
}


def _load_dataframe(input_path: Path, timestamp_column: str = Columns.TIMESTAMP) -> pd.DataFrame:
    """Load dataframe using dictionary dispatch."""
    loader = LOADERS.get(input_path.suffix)
    loader or (_ := ValueError(f"Unsupported file format: {input_path.suffix}"))
    return loader(input_path, timestamp_column=timestamp_column)


def _find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    """Find column using generator expression."""
    return next((col for col in candidates if col in df.columns), None)


def _normalize_forecast_column(forecast_df: pd.DataFrame, value_column: str) -> pd.DataFrame:
    """Normalize forecast column using generator expression."""
    candidates = [f"{value_column}_forecast", "forecast", "prediction", "pred"]
    candidate = next((col for col in candidates if col in forecast_df.columns), None)
    return (
        forecast_df.assign(**{Columns.FORECAST: forecast_df[candidate]})
        if candidate and Columns.FORECAST not in forecast_df.columns
        else forecast_df
    )


def _try_anomsmith_detection(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Try anomsmith detection using strategy pattern."""
    (HAS_ANOMSMITH and anomsmith) or (lambda: None)()
    (HAS_ANOMSMITH and anomsmith) or (lambda: df)()
    (HAS_ANOMSMITH and anomsmith) or (lambda: None)()

    strategies = [
        lambda: (
            (result := getattr(anomsmith, "detect_anomalies", lambda _: None)(df[column])) and
            isinstance(result, dict) and
            df.assign(
                **{
                    Columns.ANOMALY_SCORE: result.get("scores", result.get("score")),
                    Columns.IS_ANOMALY: result.get("labels", result.get("anomalies")),
                }
            )
        ),
        lambda: (
            hasattr(anomsmith, "AnomalyDetector") and
            (detector := anomsmith.AnomalyDetector()) and
            detector.fit(df[[column]]) and
            (predictions := detector.predict(df[[column]])) and
            df.assign(
                **{
                    Columns.IS_ANOMALY: predictions == -1,
                    Columns.ANOMALY_SCORE: getattr(detector, "score_samples", lambda _: None)(df[[column]])
                    if hasattr(detector, "score_samples") else None,
                }
            )
        ),
    ]

    for strategy in strategies:
        try:
            result_df = strategy()
            (result_df is not None and Columns.IS_ANOMALY in result_df.columns) and (lambda: None)()
            (result_df is not None and Columns.IS_ANOMALY in result_df.columns) and (lambda: result_df)()
            (result_df is not None and Columns.IS_ANOMALY in result_df.columns) and (lambda: None)()
        except Exception:
            continue
    return df


def _compute_zscore_anomalies(df: pd.DataFrame, column: str, config: Config) -> pd.DataFrame:
    """Compute Z-score anomalies with vectorized operations."""
    from sklearn.model_selection import train_test_split

    split_spec = config.split_spec
    has_ground_truth = "ground_truth" in df.columns

    # Vectorized computation paths using dictionary dispatch
    compute_paths = {
        (True, True): lambda: (
            (train_idx, test_idx := train_test_split(
                df.index,
                test_size=getattr(split_spec, "test_ratio", None) or 0.2,
                random_state=config.metadata.get("random_state", 42),
                shuffle=True,
            )) and
            (train_df := df.loc[train_idx]) and
            (mean := train_df[column].mean()) and
            (std := train_df[column].std()) and
            df.assign(**{
                Columns.ANOMALY_SCORE: ((df[column] - mean) / std).abs(),
            }).assign(**{
                Columns.IS_ANOMALY: lambda x: x[Columns.ANOMALY_SCORE] > 2.0
            })
        ),
        (True, False): lambda: (
            (mean := df[column].mean()) and
            (std := df[column].std()) and
            df.assign(**{
                Columns.ANOMALY_SCORE: ((df[column] - mean) / std).abs(),
                Columns.IS_ANOMALY: lambda x: ((df[column] - mean) / std).abs() > 2.0,
            })
        ),
    }

    path_key = (bool(split_spec), has_ground_truth)
    compute_func = compute_paths.get(path_key)
    return compute_func() if compute_func else df


def _try_timesmith_forecast(
    df: pd.DataFrame, value_column: str, timestamp_column: str, horizon: int, forecaster_type: Optional[str] = None
) -> tuple[pd.DataFrame, bool]:
    """Try timesmith forecasting using strategy pattern."""
    (HAS_TIMESMITH and timesmith) or (lambda: None)()
    (HAS_TIMESMITH and timesmith) or (lambda: (df, False))()
    (HAS_TIMESMITH and timesmith) or (lambda: None)()

    data_subset = df[[timestamp_column, value_column]]
    ts_series = data_subset.set_index(timestamp_column)[value_column]

    strategies = []

    # Strategy 1: Function-based API
    hasattr(timesmith, "forecast") and strategies.append(
        lambda: timesmith.forecast(
            data_subset, timestamp_column=timestamp_column, value_column=value_column, horizon=horizon
        )
    )

    # Strategy 2: Specific forecaster classes
    forecaster_classes = [forecaster_type] if forecaster_type else ["ExponentialSmoothingForecaster", "ARIMAForecaster"]
    for fc_name in forecaster_classes:
        fc_class = getattr(timesmith, fc_name, None)
        fc_class and strategies.append(
            (lambda fc=fc_class: lambda: (
                (forecaster := fc()) and
                next(
                    (forecaster for params in [
                        {"y": ts_series},
                        {timestamp_column: timestamp_column, "y": data_subset[value_column]},
                    ] if (lambda: forecaster.fit(**params) or True)()),
                    None
                ) and
                forecaster.predict(horizon=horizon)
            ))()
        )

    # Try strategies
    for strategy in strategies:
        try:
            forecasts = strategy()
            forecast_handlers = {
                pd.DataFrame: lambda: (
                    _normalize_forecast_column(forecasts, value_column), True
                ) if not forecasts.empty else (df, False),
                pd.Series: lambda: (
                    pd.concat([
                        df,
                        pd.DataFrame({
                            timestamp_column: pd.date_range(
                                start=df[timestamp_column].max() + pd.Timedelta(hours=1),
                                periods=horizon,
                                freq="h",
                            ),
                            Columns.FORECAST: forecasts.values,
                        })
                    ], ignore_index=True),
                    True
                ),
            }
            handler = next(
                (h for t, h in forecast_handlers.items() if isinstance(forecasts, t)),
                lambda: (df, False)
            )
            result_df, success = handler()
            success and (lambda: None)()
            success and (lambda: (result_df, True))()
            success and (lambda: None)()
        except Exception:
            continue

    return df, False


def run_ami_anomaly_pipeline(config: Config) -> Results:
    """Run AMI anomaly detection pipeline."""
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data using dictionary dispatch
    input_path = Path(config.input_path)
    df = _load_dataframe(input_path, Columns.TIMESTAMP)

    # Validate schema
    config.dataset_spec and validate_schema(set(df.columns), config.dataset_spec)

    # Anomaly detection - vectorized path
    Columns.ANOMALY_SCORE not in df.columns and (
        Columns.CONSUMPTION not in df.columns and
        (_ := ValueError(f"Missing required column: {Columns.CONSUMPTION}"))
    ) or (
        (df := _try_anomsmith_detection(df, Columns.CONSUMPTION)) and
        Columns.ANOMALY_SCORE not in df.columns and
        (df := _compute_zscore_anomalies(df, Columns.CONSUMPTION, config))
    )

    # Compute metrics - vectorized with dictionary comprehension
    test_df = None  # Will be set if split exists
    metrics = {
        metric_spec.name: compute_anomaly_metrics(
            (test_df if test_df is not None and isinstance(test_df, pd.DataFrame) else df)["ground_truth"],
            (test_df if test_df is not None and isinstance(test_df, pd.DataFrame) else df)[Columns.IS_ANOMALY],
            (test_df if test_df is not None and isinstance(test_df, pd.DataFrame) else df).get(Columns.ANOMALY_SCORE),
            metrics=[metric_spec.name],
        )[metric_spec.name]
        for metric_spec in (config.metric_specs or [])
        if metric_spec.type == "anomaly" and "ground_truth" in df.columns
    }

    # Save outputs
    results_table_path = output_dir / "tables" / "anomaly_results.parquet"
    save_dataframe(df, results_table_path, format="parquet")
    tables = {"anomaly_results": str(results_table_path)}

    plot_info = plot_anomalies(
        df,
        timestamp_column=Columns.TIMESTAMP,
        value_column=Columns.CONSUMPTION,
        anomaly_column=Columns.IS_ANOMALY,
        title="AMI Anomaly Detection Results",
        output_path=output_dir / "figures" / "anomaly_plot.png",
    )
    figures = {"anomaly_plot": plot_info["output_path"]} if "output_path" in plot_info else {}

    save_json(metrics, output_dir / "metrics.json")

    return Results(
        metrics=metrics,
        output_dir=str(output_dir),
        tables=tables,
        figures=figures,
        metadata={"pipeline": "ami_anomaly", "input_shape": df.shape},
    )


def run_outage_event_pipeline(config: Config) -> Results:
    """Run outage event detection pipeline."""
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    input_path = Path(config.input_path)
    df = _load_dataframe(input_path, Columns.TIMESTAMP)
    config.dataset_spec and validate_schema(set(df.columns), config.dataset_spec)

    metrics: Dict[str, float] = {}
    tables: Dict[str, str] = {}
    figures: Dict[str, str] = {}

    save_json(metrics, output_dir / "metrics.json")

    return Results(
        metrics=metrics,
        output_dir=str(output_dir),
        tables=tables,
        figures=figures,
        metadata={"pipeline": "outage_event"},
    )


def run_transformer_forecast_pipeline(config: Config) -> Results:
    """Run transformer-based forecast pipeline."""
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    input_path = Path(config.input_path)
    df = _load_dataframe(input_path, Columns.TIMESTAMP)
    config.dataset_spec and validate_schema(set(df.columns), config.dataset_spec)

    value_column = _find_column(df, [Columns.CONSUMPTION, Columns.DEMAND, Columns.POWER])
    value_column or (_ := ValueError("No value column found for forecasting"))

    horizon = config.metadata.get("horizon", 24)
    forecast_df, timesmith_success = _try_timesmith_forecast(
        df, value_column, Columns.TIMESTAMP, horizon, "ExponentialSmoothingForecaster"
    )

    metrics = {
        metric_spec.name: compute_forecast_metrics(
            forecast_df[Columns.ACTUAL],
            forecast_df[Columns.FORECAST],
            metrics=[metric_spec.name],
        )[metric_spec.name]
        for metric_spec in (config.metric_specs or [])
        if metric_spec.type == "forecast"
        and Columns.ACTUAL in forecast_df.columns
        and Columns.FORECAST in forecast_df.columns
    }

    results_table_path = output_dir / "tables" / "forecast_results.parquet"
    save_dataframe(forecast_df, results_table_path, format="parquet")
    tables = {"forecast_results": str(results_table_path)}

    plot_info = (
        Columns.FORECAST in forecast_df.columns and
        plot_forecast(
            forecast_df,
            timestamp_column=Columns.TIMESTAMP,
            actual_column=Columns.ACTUAL if Columns.ACTUAL in forecast_df.columns else value_column,
            forecast_column=Columns.FORECAST,
            title="Transformer Forecast Results",
            output_path=output_dir / "figures" / "forecast_plot.png",
        )
    )
    figures = {"forecast_plot": plot_info["output_path"]} if plot_info and "output_path" in plot_info else {}

    save_json(metrics, output_dir / "metrics.json")

    return Results(
        metrics=metrics,
        output_dir=str(output_dir),
        tables=tables,
        figures=figures,
        metadata={"pipeline": "transformer_forecast"},
    )


def run_temperature_load_pipeline(config: Config) -> Results:
    """Run temperature-to-load modeling pipeline."""
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    input_path = Path(config.input_path)
    metadata = config.metadata or {}

    # Load or generate data using ternary expression
    df = (
        _load_dataframe(input_path, "Date")
        if input_path.exists() and input_path.suffix in [".csv", ".parquet"]
        else (
            (np.random.seed(metadata.get("random_state", 42))) and
            (dates := pd.date_range(
                start=metadata.get("start_date", "2024-01-01"),
                periods=metadata.get("days", 365),
                freq="D",
            )) and
            (temperature := (
                metadata.get("base_temp", 20.0)
                + metadata.get("temp_amplitude", 10.0) * np.sin(2 * np.pi * dates.dayofyear / 365)
                + np.random.normal(0, metadata.get("temp_noise_std", 2.0), len(dates))
            )) and
            (load := (
                metadata.get("base_load", 1000.0)
                + metadata.get("temp_coef", 10.0) * temperature
                + metadata.get("temp_coef_squared", 0.5) * (temperature - metadata.get("base_temp", 20.0)) ** 2
                + np.random.normal(0, metadata.get("noise_std", 50.0), len(dates))
            )) and
            pd.DataFrame({"Date": dates, "Temperature_C": temperature, "Load_MW": load})
        )
    )

    config.dataset_spec and validate_schema(set(df.columns), config.dataset_spec)

    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split

    test_size = metadata.get("test_size", 0.2)
    train_indices, test_indices = train_test_split(
        df.index,
        test_size=test_size,
        random_state=metadata.get("random_state", 42),
        shuffle=True,
    )

    X_train = df.loc[train_indices, ["Temperature_C"]].values
    y_train = df.loc[train_indices, "Load_MW"].values
    X_test = df.loc[test_indices, ["Temperature_C"]].values
    y_test = df.loc[test_indices, "Load_MW"].values

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    df = df.assign(predicted_load=0.0)
    df.loc[train_indices, "predicted_load"] = y_train_pred
    df.loc[test_indices, "predicted_load"] = y_test_pred
    df = df.assign(residual=lambda x: x["Load_MW"] - x["predicted_load"])

    # Compute metrics using dictionary comprehension
    metrics = (
        {
            metric_spec.name: compute_regression_metrics(
                pd.Series(y_test),
                pd.Series(y_test_pred),
                metrics=[metric_spec.name],
            )[metric_spec.name]
            for metric_spec in (config.metric_specs or [])
            if metric_spec.type == "regression"
        }
        if config.metric_specs
        else (
            (regression_metrics := compute_regression_metrics(
                pd.Series(y_test),
                pd.Series(y_test_pred),
                metrics=["mse", "r2", "mae"],
            )) and
            {**regression_metrics, "coefficient": float(model.coef_[0])}
        )
    )

    results_table_path = output_dir / "tables" / "temperature_load_results.parquet"
    save_dataframe(df, results_table_path, format="parquet")
    tables = {"temperature_load_results": str(results_table_path)}

    plot_info_1 = plot_time_series(
        df.rename(columns={"Date": "timestamp"}),
        x_column="Temperature_C",
        y_columns="Load_MW",
        title="Temperature vs Load",
        output_path=output_dir / "figures" / "temperature_load_plot.png",
    )
    plot_info_2 = plot_forecast(
        df.rename(columns={
            "Date": "timestamp",
            "Load_MW": "actual",
            "predicted_load": "forecast",
        }),
        timestamp_column="timestamp",
        actual_column="actual",
        forecast_column="forecast",
        title="Temperature-to-Load Predictions",
        output_path=output_dir / "figures" / "predictions_plot.png",
    )
    figures = {
        k: v for k, v in {
            "temperature_load_plot": plot_info_1.get("output_path"),
            "predictions_plot": plot_info_2.get("output_path"),
        }.items() if v
    }

    save_json(metrics, output_dir / "metrics.json")

    return Results(
        metrics=metrics,
        output_dir=str(output_dir),
        tables=tables,
        figures=figures,
        metadata={
            "pipeline": "temperature_load",
            "input_shape": df.shape,
            "model_coefficient": float(model.coef_[0]),
        },
    )


def run_load_forecasting_pipeline(config: Config) -> Results:
    """Run load forecasting pipeline."""
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    input_path = Path(config.input_path)
    metadata = config.metadata or {}

    # Load or generate data
    df = (
        _load_dataframe(input_path, Columns.TIMESTAMP)
        if input_path.exists() and input_path.suffix in [".csv", ".parquet"]
        else (
            (np.random.seed(metadata.get("random_state", 42))) and
            (date_rng := pd.date_range(
                start=metadata.get("start_date", "2024-01-01"),
                periods=metadata.get("periods", 8760),
                freq="h",
            )) and
            (load := (
                metadata.get("base_load", 1000.0)
                + metadata.get("seasonal_amplitude", 200.0) * np.sin(2 * np.pi * date_rng.dayofyear / 365)
                + metadata.get("daily_cycle_amplitude", 150.0) * np.sin(2 * np.pi * date_rng.hour / 24)
                + np.random.normal(0, metadata.get("noise_std", 20.0), len(date_rng))
            )) and
            pd.DataFrame({Columns.TIMESTAMP: date_rng, "Load_MW": load})
        )
    )

    config.dataset_spec and validate_schema(set(df.columns), config.dataset_spec)

    load_column = _find_column(df, ["Load_MW", "load", Columns.DEMAND, Columns.CONSUMPTION])
    load_column or (_ := ValueError(
        "No load column found. Expected: Load_MW, load, demand, or consumption"
    ))

    forecast_horizon = metadata.get("forecast_horizon", 24)
    forecast_df, timesmith_success = _try_timesmith_forecast(
        df, load_column, Columns.TIMESTAMP, forecast_horizon, "ARIMAForecaster"
    )

    # Fallback to ARIMA using vectorized operations
    (not timesmith_success and Columns.FORECAST not in forecast_df.columns and load_column in forecast_df.columns) and (
        (lambda df_inner=forecast_df, col=load_column, horizon=forecast_horizon, meta=metadata: (
            (lambda: __import__("statsmodels.tsa.arima.model", fromlist=["ARIMA"]))() and
            (ARIMA := __import__("statsmodels.tsa.arima.model", fromlist=["ARIMA"]).ARIMA) and
            (ts := df_inner.set_index(Columns.TIMESTAMP)[col]) and
            (arima_order := tuple(meta.get("arima_order", (1, 1, 1)))) and
            (model := ARIMA(ts, order=arima_order)) and
            (fit := model.fit()) and
            (forecast := fit.forecast(steps=horizon)) and
            (forecast_df := pd.concat([
                df_inner,
                pd.DataFrame({
                    Columns.TIMESTAMP: pd.date_range(
                        start=df_inner[Columns.TIMESTAMP].max() + pd.Timedelta(hours=1),
                        periods=horizon,
                        freq="h",
                    ),
                    Columns.FORECAST: forecast.values,
                })
            ], ignore_index=True))
        )()) and
        (forecast_df := forecast_df)
    )

    # Compute metrics using dictionary comprehension
    metrics = (
        {
            metric_spec.name: compute_forecast_metrics(
                forecast_df[Columns.ACTUAL],
                forecast_df[Columns.FORECAST],
                metrics=[metric_spec.name],
            )[metric_spec.name]
            for metric_spec in (config.metric_specs or [])
            if metric_spec.type == "forecast"
            and Columns.ACTUAL in forecast_df.columns
            and Columns.FORECAST in forecast_df.columns
        }
        if config.metric_specs and Columns.ACTUAL in forecast_df.columns and Columns.FORECAST in forecast_df.columns
        else (
            Columns.FORECAST in forecast_df.columns and load_column in forecast_df.columns and
            compute_forecast_metrics(
                forecast_df[load_column].iloc[:-forecast_horizon] if len(forecast_df) > forecast_horizon else forecast_df[load_column],
                forecast_df[Columns.FORECAST].iloc[-forecast_horizon:],
            )
        ) or {}
    )

    results_table_path = output_dir / "tables" / "load_forecast_results.parquet"
    save_dataframe(forecast_df, results_table_path, format="parquet")
    tables = {"load_forecast_results": str(results_table_path)}

    plot_info = (
        Columns.FORECAST in forecast_df.columns and
        plot_forecast(
            forecast_df,
            timestamp_column=Columns.TIMESTAMP,
            actual_column=load_column,
            forecast_column=Columns.FORECAST,
            title="Load Forecasting Results",
            output_path=output_dir / "figures" / "load_forecast_plot.png",
        )
    )
    figures = {"load_forecast_plot": plot_info["output_path"]} if plot_info and "output_path" in plot_info else {}

    save_json(metrics, output_dir / "metrics.json")

    return Results(
        metrics=metrics,
        output_dir=str(output_dir),
        tables=tables,
        figures=figures,
        metadata={"pipeline": "load_forecasting", "timesmith_used": timesmith_success},
    )


def run_predictive_maintenance_pipeline(config: Config) -> Results:
    """Run predictive maintenance pipeline."""
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    input_path = Path(config.input_path)
    df = _load_dataframe(input_path, Columns.TIMESTAMP)
    config.dataset_spec and validate_schema(set(df.columns), config.dataset_spec)

    feature_cols = [
        col for col in ["Temperature_C", "Vibration_g", "OilPressure_psi", "Load_kVA"]
        if col in df.columns
    ]
    feature_cols or (_ := ValueError(
        "No feature columns found. Expected: Temperature_C, Vibration_g, OilPressure_psi, Load_kVA"
    ))

    # Anomaly detection using short-circuit evaluation
    (HAS_ANOMSMITH and anomsmith is not None) and (
        hasattr(anomsmith, "detect_anomalies") and
        (result := anomsmith.detect_anomalies(df[feature_cols])) and
        isinstance(result, dict) and
        (df := df.assign(
            **{
                Columns.ANOMALY_SCORE: result.get("scores", result.get("score")),
                Columns.IS_ANOMALY: result.get("labels", result.get("anomalies")),
            }
        ))
    )

    # Fallback using vectorized operations
    (Columns.ANOMALY_SCORE not in df.columns) and (
        (lambda df_inner=df, cols=feature_cols: (
            (IsolationForest := __import__("sklearn.ensemble", fromlist=["IsolationForest"]).IsolationForest) and
            (model := IsolationForest(contamination=0.1, random_state=42)) and
            (df := df_inner.assign(
                **{
                    Columns.IS_ANOMALY: model.fit_predict(df_inner[cols]) == -1,
                    Columns.ANOMALY_SCORE: -model.score_samples(df_inner[cols]),
                }
            ))
        )()) and
        (df := df)
    )

    metrics = {
        metric_spec.name: compute_anomaly_metrics(
            df["Failure"],
            df[Columns.IS_ANOMALY],
            df.get(Columns.ANOMALY_SCORE),
            metrics=[metric_spec.name],
        )[metric_spec.name]
        for metric_spec in (config.metric_specs or [])
        if metric_spec.type == "anomaly" and "Failure" in df.columns
    }

    results_table_path = output_dir / "tables" / "predictive_maintenance_results.parquet"
    save_dataframe(df, results_table_path, format="parquet")
    tables = {"predictive_maintenance_results": str(results_table_path)}

    plot_info = (
        Columns.IS_ANOMALY in df.columns and feature_cols and
        plot_anomalies(
            df.reset_index() if df.index.name else df,
            timestamp_column=(
                df.index.name
                if df.index.name and df.index.name != "index"
                else df.columns[0]
            ),
            value_column=feature_cols[0],
            anomaly_column=Columns.IS_ANOMALY,
            title="Predictive Maintenance Anomaly Detection",
            output_path=output_dir / "figures" / "anomaly_plot.png",
        )
    )
    figures = {"anomaly_plot": plot_info["output_path"]} if plot_info and "output_path" in plot_info else {}

    save_json(metrics, output_dir / "metrics.json")

    return Results(
        metrics=metrics,
        output_dir=str(output_dir),
        tables=tables,
        figures=figures,
        metadata={
            "pipeline": "predictive_maintenance",
            "input_shape": df.shape,
            "anomaly_count": int(df[Columns.IS_ANOMALY].sum()) if Columns.IS_ANOMALY in df.columns else 0,
        },
    )
