# How to Run GridSmith Pipelines

This guide explains how to run GridSmith pipelines using different methods.

## Prerequisites

1. Install GridSmith:
```bash
pip install gridsmith
```

2. Ensure you have data files in the expected format (see [Data Formats](data.md))

## Running via CLI

The CLI is the simplest way to run pipelines.

### Basic Usage

```bash
gridsmith run <pipeline-name> --config <config-file.yaml>
```

### Available Pipelines

- `ami-anomaly`: AMI anomaly detection
- `temperature-load`: Temperature-to-load modeling
- `load-forecasting`: Load forecasting
- `predictive-maintenance`: Predictive maintenance
- `outage-prediction`: Outage prediction
- `outage-detect`: Outage event detection
- `asset-degradation`: Asset degradation analysis
- `load-shape`: Load shape analysis

### Example

```bash
gridsmith run ami-anomaly --config configs/ami_anomaly.yaml
```

### Validate Config

Before running, validate your config file:

```bash
gridsmith validate --config configs/ami_anomaly.yaml
```

### Get Help

```bash
gridsmith info
gridsmith run --help
```

## Running via Python API

For programmatic access, use the Python API:

```python
from gridsmith import GridSmithClient
from gridsmith.api.config import AMIAnomalyConfig

# Create client
client = GridSmithClient()

# Create config
config = AMIAnomalyConfig(
    input_path="data/ami_data.csv",
    output_dir="runs/output",
    timestamp_column="timestamp",
    value_column="consumption",
    meter_id_column="meter_id",
)

# Run pipeline
results = client.ami_anomaly(config)

# Access results
print(f"Metrics: {results.metrics}")
print(f"Output directory: {results.output_dir}")
print(f"Tables: {results.tables}")
print(f"Figures: {results.figures}")
```

## Running Example Scripts

Each example has a `run.py` script:

```bash
cd examples/ami_anomaly
python run.py
```

## Config File Format

Config files are YAML. Example:

```yaml
input_path: data/ami_data.csv
output_dir: runs/output
timestamp_column: timestamp
value_column: consumption
meter_id_column: meter_id
metadata:
  chapter: 1
  pipeline: ami_anomaly
```

## Output Structure

All outputs are written to the specified output directory:

```
runs/<timestamp>_<pipeline_name>/
├── metrics.json          # Evaluation metrics
├── tables/               # Output tables (Parquet)
│   └── ...
├── figures/              # Generated plots
│   └── ...
└── logs/                 # Log files (if any)
```

## Troubleshooting

### Config Validation Errors

If you see config validation errors:
1. Check that all required fields are present
2. Verify file paths exist
3. Use `gridsmith validate --config <file>` to debug

### Missing Dependencies

If you see import errors:
1. Ensure all Smith libraries are installed
2. Check that minimal versions are met
3. Install from requirements: `pip install -r requirements.txt`

### Data Format Issues

If you see schema validation errors:
1. Check column names match expected names
2. Verify timestamp column can be parsed as datetime
3. Ensure required columns are present

