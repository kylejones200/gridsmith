# Chapter 1: AMI Anomaly Detection

This example demonstrates AMI (Advanced Metering Infrastructure) anomaly detection as described in ML4U Chapter 1.

## Overview

The AMI anomaly detection pipeline:
1. Loads AMI meter data
2. Detects anomalies in consumption patterns
3. Computes evaluation metrics
4. Generates visualizations

## Input Data

The pipeline expects a CSV or Parquet file with the following columns:
- `timestamp`: Timestamp of the measurement
- `consumption`: Energy consumption value
- `meter_id` (optional): Unique identifier for the meter

## Running the Example

### Using the CLI

```bash
gridsmith run ami-anomaly --config ../../configs/ch01_ami_anomaly.yaml
```

### Using Python

```python
from gridsmith import GridSmithClient
from gridsmith.api.config import AMIAnomalyConfig

client = GridSmithClient()
config = AMIAnomalyConfig(
    input_path="data/ami_data.csv",
    output_dir="../../runs/ch01_ami_anomaly",
    timestamp_column="timestamp",
    value_column="consumption",
    meter_id_column="meter_id",
)

results = client.ami_anomaly(config)
print(f"Metrics: {results.metrics}")
print(f"Output directory: {results.output_dir}")
```

### Using the run script

```bash
python run.py
```

## Output Artifacts

The pipeline generates the following outputs in the `runs/<timestamp>_ch01_ami_anomaly/` directory:

- `metrics.json`: Evaluation metrics (precision, recall, F1)
- `tables/anomaly_results.parquet`: Full results with anomaly scores and labels
- `figures/anomaly_plot.png`: Visualization of anomalies

## Expected Artifacts

See `expected_artifacts.md` for detailed schema and metric information.

## Testing

Run the test suite to validate the example:

```bash
pytest tests/test_ch01_ami_anomaly.py
```

