# Data Formats

This document describes the expected input data formats for GridSmith pipelines.

## General Data Requirements

GridSmith accepts data in CSV or Parquet format. Timestamp columns should be parseable as datetime objects.

## Common Columns

GridSmith uses canonical column names defined in `core/contracts.py`:

### Time Columns
- `timestamp`: Primary timestamp column
- `datetime`: Alternative timestamp column name
- `date`: Date column

### Identifier Columns
- `meter_id`: Meter identifier
- `ami_id`: AMI identifier
- `asset_id`: Asset identifier
- `location_id`: Location identifier
- `customer_id`: Customer identifier

### Measurement Columns
- `consumption`: Energy consumption
- `demand`: Power demand
- `voltage`: Voltage measurement
- `current`: Current measurement
- `power`: Power measurement
- `energy`: Energy measurement

### Anomaly Columns
- `is_anomaly`: Binary anomaly label
- `anomaly_score`: Anomaly score (continuous)
- `anomaly_type`: Type of anomaly

## AMI Anomaly Detection

### Required Columns
- `timestamp`: Timestamp of measurement (datetime)
- `consumption`: Energy consumption value (numeric)

### Optional Columns
- `meter_id`: Meter identifier (string)
- `ground_truth`: Ground truth anomaly labels (binary, for evaluation)

### Example Data

```csv
timestamp,consumption,meter_id
2024-01-01 00:00:00,100.5,meter_001
2024-01-01 01:00:00,102.3,meter_001
2024-01-01 02:00:00,99.8,meter_001
...
```

### Schema Validation

The pipeline validates:
1. Required columns are present
2. Timestamp column can be parsed as datetime
3. Value columns are numeric

## Outage Detection

### Required Columns
- `timestamp`: Timestamp of measurement

### Optional Columns
- `voltage`: Voltage measurements
- `power`: Power measurements
- `location_id`: Location identifier

## Asset Degradation

### Required Columns
- `timestamp`: Timestamp of measurement
- `asset_id`: Asset identifier

### Optional Columns
- `condition_score`: Condition score
- `temperature`: Temperature measurement
- `vibration`: Vibration measurement

## Load Shape Analysis

### Required Columns
- `timestamp`: Timestamp of measurement
- `consumption`: Consumption values

### Optional Columns
- `customer_id`: Customer identifier
- `location_id`: Location identifier

## Data Preprocessing

GridSmith performs minimal preprocessing:
- Timestamp parsing
- Basic schema validation
- Missing value handling (varies by pipeline)

For more complex preprocessing, users should preprocess data before passing to GridSmith.

## File Formats

### CSV
- Header row required
- UTF-8 encoding recommended
- Timestamp format: ISO 8601 preferred, but flexible

### Parquet
- Recommended for large datasets
- Supports better type preservation
- Faster I/O

## Examples

Sample data files are provided in each chapter's example directory:
- `examples/ami_anomaly/data/ami_data.csv`

