# Smith Library Integration

GridSmith integrates with the Smith library ecosystem to provide ML capabilities:

- **timesmith**: Time series forecasting and analysis
- **anomsmith**: Anomaly detection
- **plotsmith**: Data visualization

## Integration Strategy

GridSmith uses a **graceful fallback** approach:

1. **Try to import** Smith libraries at module level
2. **Attempt to use** Smith library APIs when available
3. **Fall back** to local implementations if libraries are not installed or fail

This allows GridSmith to:
- Work with Smith libraries when they're available
- Continue functioning even if Smith libraries aren't installed (using placeholders)
- Support gradual adoption as Smith libraries are developed

## How It Works

### Anomaly Detection (anomsmith)

In `core/pipelines.py`, the AMI anomaly pipeline:

```python
if HAS_ANOMSMITH and anomsmith is not None:
    try:
        # Try various anomsmith API patterns
        if hasattr(anomsmith, "detect_anomalies"):
            result = anomsmith.detect_anomalies(...)
        elif hasattr(anomsmith, "AnomalyDetector"):
            detector = anomsmith.AnomalyDetector()
            detector.fit(...)
            predictions = detector.predict(...)
    except Exception:
        # Fall back to simple threshold-based detection
        pass
```

### Time Series Forecasting (timesmith)

In `core/pipelines.py`, the transformer forecast pipeline:

```python
if HAS_TIMESMITH and timesmith is not None:
    try:
        # Try various timesmith API patterns
        if hasattr(timesmith, "forecast"):
            forecasts = timesmith.forecast(...)
        elif hasattr(timesmith, "Forecaster"):
            forecaster = timesmith.Forecaster()
            forecaster.fit(...)
            forecasts = forecaster.predict(...)
    except Exception:
        # Fall back to placeholder
        pass
```

### Visualization (plotsmith)

In `core/plots.py`, all plotting functions:

```python
if HAS_PLOTSMITH and plotsmith is not None:
    try:
        # Try various plotsmith API patterns
        if hasattr(plotsmith, "plot_anomalies"):
            fig = plotsmith.plot_anomalies(...)
        elif hasattr(plotsmith, "plot") and hasattr(plotsmith.plot, "anomalies"):
            fig = plotsmith.plot.anomalies(...)
    except Exception:
        # Fall back to metadata-only response
        pass
```

### Metrics (timesmith & anomsmith)

In `core/eval.py`, metric computation:

```python
if HAS_TIMESMITH and timesmith is not None:
    try:
        # Try timesmith metrics
        if hasattr(timesmith, "compute_forecast_metrics"):
            return timesmith.compute_forecast_metrics(...)
    except Exception:
        # Fall back to local computation
        return compute_regression_metrics(...)
```

## Supported API Patterns

GridSmith attempts to use these common API patterns:

### Anomaly Detection

- `anomsmith.detect_anomalies(data)` - Function-based API
- `anomsmith.AnomalyDetector()` - Class-based API (sklearn-style)
- `anomsmith.fit_predict()` - Direct function call

### Time Series Forecasting

- `timesmith.forecast(data, horizon)` - Function-based API
- `timesmith.Forecaster()` - Class-based API
- `timesmith.compute_forecast_metrics()` - Metrics API

### Visualization

- `plotsmith.plot_anomalies(...)` - Function-based API
- `plotsmith.plot.anomalies(...)` - Namespace-based API

## Benefits

1. **Flexible**: Works with or without Smith libraries
2. **Extensible**: Easy to add new Smith library integrations
3. **Robust**: Graceful error handling prevents pipeline failures
4. **Progressive**: Can adopt Smith libraries incrementally

## Usage

### With Smith Libraries Installed

```bash
pip install timesmith anomsmith plotsmith
gridsmith run ami-anomaly --config configs/ch01_ami_anomaly.yaml
```

GridSmith will automatically use Smith libraries when available.

### Without Smith Libraries

```bash
# Don't install Smith libraries
gridsmith run ami-anomaly --config configs/ch01_ami_anomaly.yaml
```

GridSmith will use fallback implementations (placeholders).

## Future Enhancements

As Smith libraries mature, GridSmith will:

1. Add more specific API pattern detection
2. Support configuration for selecting algorithms
3. Add more comprehensive error messages when libraries fail
4. Document expected Smith library API contracts

## Integration with electric_utilities

GridSmith is designed to work alongside the `electric_utilities` repository:

- **electric_utilities**: Production ML code using sklearn, tensorflow, etc.
- **GridSmith**: Orchestration layer using Smith libraries for composability

Both can coexist and share:
- Data formats (Parquet, CSV)
- Configuration patterns
- Output structures

GridSmith provides a cleaner, more composable interface by delegating to Smith libraries instead of directly using sklearn/tensorflow.

