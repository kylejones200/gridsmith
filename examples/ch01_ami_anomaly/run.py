"""Run script for AMI Anomaly Detection example."""

from datetime import datetime
from pathlib import Path

import yaml

from gridsmith import GridSmithClient
from gridsmith.api.config import AMIAnomalyConfig

# Get the example directory
example_dir = Path(__file__).parent
config_path = example_dir.parent.parent / "configs" / "ami_anomaly.yaml"

# Load config from YAML
with open(config_path) as f:
    config_dict = yaml.safe_load(f)

# Create config object
config = AMIAnomalyConfig(**config_dict)

# Create output directory with timestamp

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = Path("../../runs") / f"{timestamp}_ami_anomaly"
config.output_dir = str(output_dir)

# Run pipeline
print("Running AMI anomaly detection pipeline...")
client = GridSmithClient()
results = client.ami_anomaly(config)

print("\n✓ Pipeline completed successfully!")
print(f"  Output directory: {results.output_dir}")
print(f"  Metrics computed: {list(results.metrics.keys())}")
print(f"  Tables generated: {list(results.tables.keys())}")
print(f"  Figures generated: {list(results.figures.keys())}")

if results.metrics:
    print("\nMetrics:")
    for name, value in results.metrics.items():
        print(f"  {name}: {value:.4f}")
