# Chapter 1: AMI Anomaly Detection

This chapter implements AMI (Advanced Metering Infrastructure) anomaly detection as described in ML4U Chapter 1.

## Overview

The AMI anomaly detection pipeline identifies anomalous patterns in smart meter consumption data. It uses algorithms from `anomsmith` to detect outliers and irregular consumption patterns.

## Pipeline Steps

1. **Data Loading**: Load AMI meter data from CSV or Parquet
2. **Schema Validation**: Validate required columns and data types
3. **Anomaly Detection**: Apply anomaly detection algorithms (from anomsmith)
4. **Metric Computation**: Compute evaluation metrics (precision, recall, F1)
5. **Visualization**: Generate time series plots with anomaly markers

## Configuration

Example config (`configs/ch01_ami_anomaly.yaml`):

```yaml
input_path: examples/ch01_ami_anomaly/data/ami_data.csv
output_dir: runs/ch01_ami_anomaly
timestamp_column: timestamp
value_column: consumption
meter_id_column: meter_id
metadata:
  chapter: 1
  pipeline: ami_anomaly
```

## Input Data

Required columns:
- `timestamp`: Timestamp of measurement
- `consumption`: Energy consumption value

Optional columns:
- `meter_id`: Meter identifier
- `ground_truth`: Ground truth labels (for evaluation)

## Output Artifacts

- `metrics.json`: Evaluation metrics (if ground truth provided)
- `tables/anomaly_results.parquet`: Full results with scores and labels
- `figures/anomaly_plot.png`: Visualization of anomalies

## Running the Example

### CLI

```bash
gridsmith run ami-anomaly --config configs/ch01_ami_anomaly.yaml
```

### Python

```python
from gridsmith import GridSmithClient
from gridsmith.api.config import AMIAnomalyConfig

client = GridSmithClient()
config = AMIAnomalyConfig(
    input_path="data/ami_data.csv",
    output_dir="runs/output",
)

results = client.ami_anomaly(config)
```

## Metrics

If ground truth labels are provided, the pipeline computes:
- `precision`: Precision score
- `recall`: Recall score
- `f1`: F1 score

## Algorithm Details

The pipeline uses `anomsmith` for anomaly detection. Current implementation uses a placeholder threshold-based method. Future versions will integrate full anomsmith algorithms.

## Expected Results

See `examples/ch01_ami_anomaly/expected_artifacts.md` for detailed schema and validation criteria.

