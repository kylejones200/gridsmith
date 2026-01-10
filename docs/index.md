# GridSmith Documentation

GridSmith is an orchestration and reference app layer for ML4U (Machine Learning for Utilities) chapter examples. It provides a clean interface to compose algorithms from the Smith library ecosystem.

## Overview

GridSmith is organized into four layers:

1. **Core Layer**: Domain objects, configs, and pipelines that compose Smith libraries
2. **API Layer**: Stable public interface with user-friendly entrypoints
3. **CLI Layer**: Terminal interface for running pipelines
4. **Examples Layer**: Runnable chapter examples with documentation

## Quick Start

### Installation

```bash
pip install gridsmith
```

### Running a Pipeline

Using the CLI:

```bash
gridsmith run ami-anomaly --config configs/ch01_ami_anomaly.yaml
```

Using Python:

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

## Available Pipelines

GridSmith supports all ML4U book chapters (28+ pipelines). Here are the key pipelines:

**Core Applications:**
- **ami-anomaly**: AMI anomaly detection
- **temperature-load**: Temperature-to-load modeling (Chapter 1)
- **load-forecasting**: Load forecasting with ARIMA/LSTM (Chapter 4)
- **predictive-maintenance**: Asset health monitoring (Chapter 5)
- **outage-prediction**: Storm outage prediction (Chapter 6)
- **grid-optimization**: Grid optimization with RL (Chapter 7)
- **der-forecasting**: Distributed energy resource forecasting (Chapter 8)
- **demand-response**: Customer load profiling (Chapter 9)

**Advanced Techniques:**
- **computer-vision**: Vegetation detection (Chapter 10)
- **nlp**: Log classification (Chapter 11)
- **ai-utilities**: LLM integration (Chapter 12)
- **geospatial**: Feeder mapping, asset location (Chapter 13)

**Integration & Scale:**
- **mlops**: MLflow integration (Chapter 14)
- **cybersecurity**: Threat detection (Chapter 17)
- **ethics**: Fairness auditing (Chapter 18)
- **roi-analysis**: Cost-benefit analysis (Chapter 19)
- **realtime-analytics**: Streaming analytics (Chapter 22)
- **compliance**: SAIDI/SAIFI reporting (Chapter 23)
- **feature-engineering**: Temporal, geospatial features (Chapter 24)
- **reliability**: Reliability analytics (Chapter 25)
- **market-operations**: Price forecasting, bidding (Chapter 26)

**Advanced Research:**
- **causal-inference**: Causal methods (Chapter 27)
- **multi-task-learning**: MTL models (Chapter 28)

## Documentation

- [Architecture](architecture.md) - System design and layer organization
- [How to Run](how_to_run.md) - Detailed usage instructions
- [Data Formats](data.md) - Input data requirements
- [Integration](integration.md) - Smith library integration guide
- [Chapter Examples](../examples/) - Chapter-specific examples

## Contributing

GridSmith focuses on orchestration, not algorithms. New algorithms belong in the Smith libraries (timesmith, anomsmith, geosmith, ressmith, plotsmith).

## License

MIT License

