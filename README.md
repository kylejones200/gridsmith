# GridSmith

Orchestration and reference app layer for ML4U (Machine Learning for Utilities) chapter examples.

## Overview

GridSmith provides a clean, layered architecture for running ML4U chapter examples. It composes algorithms from the Smith library ecosystem (timesmith, anomsmith, geosmith, ressmith, plotsmith) without implementing new algorithms itself.

## Architecture

GridSmith is organized into four layers:

1. **Core Layer**: Domain objects, configs, and pipelines that compose Smith libraries
2. **API Layer**: Stable public interface with user-friendly entrypoints
3. **CLI Layer**: Terminal interface for running pipelines
4. **Examples Layer**: Runnable chapter examples with documentation

## Quick Start

### Installation

Basic installation:

```bash
pip install gridsmith
```

With Smith libraries (recommended for full functionality):

```bash
pip install gridsmith[smith]
# or
pip install -r requirements-smith.txt
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

GridSmith provides machine learning pipelines for utility operations. Here are the available pipelines:

### Core Applications (Part II)

- **ami-anomaly**: AMI anomaly detection
- **temperature-load**: Temperature-to-load modeling
- **ml-fundamentals**: Regression, classification, clustering
- **load-forecasting**: Load forecasting with ARIMA/LSTM
- **predictive-maintenance**: Asset health monitoring
- **outage-prediction**: Storm outage prediction
- **grid-optimization**: Grid optimization with RL
- **der-forecasting**: Distributed energy resource forecasting
- **demand-response**: Customer load profiling

### Advanced Techniques (Part III)

- **computer-vision**: Vegetation detection, PLD
- **nlp**: Log classification, entity extraction
- **ai-utilities**: LLM integration
- **geospatial**: Feeder mapping, asset location

### Integration & Scale (Part IV)

- **mlops**: MLflow integration, model registry
- **cybersecurity**: Threat detection
- **ethics**: Fairness auditing
- **roi-analysis**: Cost-benefit analysis
- **realtime-analytics**: Streaming analytics
- **compliance**: SAIDI/SAIFI reporting
- **feature-engineering**: Temporal, geospatial features
- **reliability**: Reliability analytics
- **market-operations**: Price forecasting, bidding

### Advanced Research

- **causal-inference**: Difference-in-differences, synthetic control
- **multi-task-learning**: MTL models

See [Documentation](docs/index.md) for more details.

## Project Structure

```text
gridsmith/
├── src/gridsmith/
│   ├── core/          # Layer 1: Domain objects and pipelines
│   ├── api/           # Layer 2: Public interface
│   └── cli/           # Layer 3: Command-line interface
├── examples/          # Layer 4: Chapter examples
├── configs/           # Configuration files
├── docs/              # Documentation
└── tests/             # Test suite
```

## Development

### Setup

```bash
git clone <repository>
cd gridsmith
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Linting

```bash
ruff check .
```

### Type Checking

```bash
mypy src/gridsmith
```

## Documentation

- [Architecture](docs/architecture.md) - System design and layer organization
- [How to Run](docs/how_to_run.md) - Detailed usage instructions
- [Data Formats](docs/data.md) - Input data requirements
- [Chapter Examples](examples/) - Chapter-specific examples

## Design Principles

1. **No new algorithms**: GridSmith orchestrates existing Smith libraries
2. **Pure orchestration**: Core layer composes, doesn't compute
3. **Stable API**: Public interface hides internal structure
4. **Runnable examples**: Every chapter has a working example
5. **Testable**: Golden tests validate schema and metrics

## Definition of Done

- ✅ Can run one command from a clean venv
- ✅ Get metrics, tables, and figures in a run folder
- ✅ README explains inputs and outputs
- ✅ Test asserts schema and metric keys

## Integration Policy

GridSmith integrates with the Smith library ecosystem:

- **timesmith**: Time series forecasting and analysis
- **anomsmith**: Anomaly detection
- **plotsmith**: Data visualization

GridSmith uses **graceful fallback** - it works with or without Smith libraries installed:

- Attempts to use Smith libraries when available
- Falls back to local implementations if libraries are missing
- Supports multiple API patterns for maximum compatibility

See [Integration Guide](docs/integration.md) for details.

### Dependencies

GridSmith depends on Smith libs by version:

- Pin minimal versions
- Avoid tight coupling to internal modules
- Import from public APIs only
- Graceful degradation if libraries unavailable

## License

MIT License
