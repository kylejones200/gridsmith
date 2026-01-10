# GridSmith Documentation

GridSmith is an orchestration and reference app layer for machine learning in utilities. It provides a clean interface to compose algorithms from the Smith library ecosystem.

## Overview

GridSmith is organized into four layers:

1. **Core Layer**: Domain objects, configs, and pipelines that compose Smith libraries
2. **API Layer**: Stable public interface with user-friendly entrypoints
3. **CLI Layer**: Terminal interface for running pipelines
4. **Examples Layer**: Runnable examples with documentation

## Quick Start

### Installation

```bash
pip install gridsmith
```

### Running a Pipeline

Using the CLI:

```bash
gridsmith run ami-anomaly --config configs/ami_anomaly.yaml
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

GridSmith provides machine learning pipelines for utility operations. Here are the key pipelines:

**Core Applications:**
- **ami-anomaly**: AMI anomaly detection
- **temperature-load**: Temperature-to-load modeling
- **load-forecasting**: Load forecasting with ARIMA/LSTM
- **predictive-maintenance**: Asset health monitoring
- **outage-prediction**: Storm outage prediction
- **grid-optimization**: Grid optimization with RL
- **der-forecasting**: Distributed energy resource forecasting
- **demand-response**: Customer load profiling

**Advanced Techniques:**
- **computer-vision**: Vegetation detection
- **nlp**: Log classification
- **ai-utilities**: LLM integration
- **geospatial**: Feeder mapping, asset location

**Integration & Scale:**
- **mlops**: MLflow integration
- **cybersecurity**: Threat detection
- **ethics**: Fairness auditing
- **roi-analysis**: Cost-benefit analysis
- **realtime-analytics**: Streaming analytics
- **compliance**: SAIDI/SAIFI reporting
- **feature-engineering**: Temporal, geospatial features
- **reliability**: Reliability analytics
- **market-operations**: Price forecasting, bidding

**Advanced Research:**
- **causal-inference**: Causal methods
- **multi-task-learning**: MTL models

## Documentation

- [Architecture](architecture.md) - System design and layer organization
- [How to Run](how_to_run.md) - Detailed usage instructions
- [Data Formats](data.md) - Input data requirements
- [Integration](integration.md) - Smith library integration guide
- [Examples](../examples/) - Example pipelines

## Contributing

GridSmith focuses on orchestration, not algorithms. New algorithms belong in the Smith libraries (timesmith, anomsmith, geosmith, ressmith, plotsmith).

## License

MIT License

