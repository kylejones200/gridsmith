# Expected Artifacts for Chapter 1: AMI Anomaly Detection

This document describes the expected output artifacts from the AMI anomaly detection pipeline.

## Output Directory Structure

```
runs/<timestamp>_ch01_ami_anomaly/
├── metrics.json
├── tables/
│   └── anomaly_results.parquet
├── figures/
│   └── anomaly_plot.png
└── logs/
```

## metrics.json

Schema:
```json
{
  "precision": <float>,
  "recall": <float>,
  "f1": <float>
}
```

Description:
- `precision`: Precision score (only if ground truth labels are available)
- `recall`: Recall score (only if ground truth labels are available)
- `f1`: F1 score (only if ground truth labels are available)

Note: If ground truth labels are not provided, metrics will be empty.

## tables/anomaly_results.parquet

Schema:
| Column | Type | Description |
|--------|------|-------------|
| timestamp | datetime64[ns] | Timestamp of measurement |
| consumption | float64 | Energy consumption value |
| meter_id | object (optional) | Meter identifier |
| anomaly_score | float64 | Anomaly score (higher = more anomalous) |
| is_anomaly | bool | Binary anomaly label |

## figures/anomaly_plot.png

A time series plot showing:
- Consumption values over time
- Marked anomalies (if detected)
- Anomaly thresholds

## Validation

The test suite validates:
1. All expected files exist
2. metrics.json has the expected schema
3. anomaly_results.parquet has the expected columns
4. Metric values are within expected ranges

