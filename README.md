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

GridSmith supports all ML4U book chapters. Here are the core pipelines:

### Core Applications (Part II)

- **ami-anomaly**: AMI anomaly detection
- **temperature-load**: Temperature-to-load modeling (Chapter 1)
- **ml-fundamentals**: Regression, classification, clustering (Chapter 3)
- **load-forecasting**: Load forecasting with ARIMA/LSTM (Chapter 4)
- **predictive-maintenance**: Asset health monitoring (Chapter 5)
- **outage-prediction**: Storm outage prediction (Chapter 6)
- **grid-optimization**: Grid optimization with RL (Chapter 7)
- **der-forecasting**: Distributed energy resource forecasting (Chapter 8)
- **demand-response**: Customer load profiling (Chapter 9)

### Advanced Techniques (Part III)

- **computer-vision**: Vegetation detection, PLD (Chapter 10)
- **nlp**: Log classification, entity extraction (Chapter 11)
- **ai-utilities**: LLM integration (Chapter 12)
- **geospatial**: Feeder mapping, asset location (Chapter 13)

### Integration & Scale (Part IV)

- **mlops**: MLflow integration, model registry (Chapter 14)
- **cybersecurity**: Threat detection (Chapter 17)
- **ethics**: Fairness auditing (Chapter 18)
- **roi-analysis**: Cost-benefit analysis (Chapter 19)
- **realtime-analytics**: Streaming analytics (Chapter 22)
- **compliance**: SAIDI/SAIFI reporting (Chapter 23)
- **feature-engineering**: Temporal, geospatial features (Chapter 24)
- **reliability**: Reliability analytics (Chapter 25)
- **market-operations**: Price forecasting, bidding (Chapter 26)

### Advanced Research

- **causal-inference**: Difference-in-differences, synthetic control (Chapter 27)
- **multi-task-learning**: MTL models (Chapter 28)

GridSmith supports all 28+ chapters from the ML4U book. See [Documentation](docs/index.md) for more details.

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

## Definition of Done for Chapter 1

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
