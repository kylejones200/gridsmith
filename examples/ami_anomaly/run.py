"""Run script for AMI Anomaly Detection example."""

from pathlib import Path

from gridsmith import GridSmithClient
from gridsmith.api.config import AMIAnomalyConfig

# Get the example directory
example_dir = Path(__file__).parent
config_path = example_dir.parent.parent / "configs" / "ami_anomaly.yaml"

# Load config from YAML
import yaml

with open(config_path, "r") as f:
    config_dict = yaml.safe_load(f)

# Create config object
config = AMIAnomalyConfig(**config_dict)

# Create output directory with timestamp
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = Path("../../runs") / f"{timestamp}_ami_anomaly"
config.output_dir = str(output_dir)

# Run pipeline
print("Running AMI anomaly detection pipeline...")
client = GridSmithClient()
results = client.ami_anomaly(config)

print(f"\n✓ Pipeline completed successfully!")
print(f"  Output directory: {results.output_dir}")
print(f"  Metrics computed: {list(results.metrics.keys())}")
print(f"  Tables generated: {list(results.tables.keys())}")
print(f"  Figures generated: {list(results.figures.keys())}")

if results.metrics:
    print(f"\nMetrics:")
    for name, value in results.metrics.items():
        print(f"  {name}: {value:.4f}")

