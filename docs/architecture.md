# GridSmith Architecture

GridSmith is organized into four distinct layers, each with a specific responsibility.

## Layer 1: Core

**Purpose**: Define domain objects, configs, and pipelines that compose other Smith libraries.

**Directory**: `src/gridsmith/core/`

**Rules**:
- Core imports from timesmith, anomsmith, geosmith, ressmith, plotsmith
- Core exposes pure Python functions and dataclasses
- Core stays I/O light - pass paths or file-like objects in
- Core returns standard objects - prefer pandas DataFrame and plain dict
- Core owns no model math - algorithms stay in Smith libs

### Core Modules

- `contracts.py`: Canonical column names and schema checks. Domain objects (DatasetSpec, FeatureSpec, SplitSpec, MetricSpec)
- `pipelines.py`: Chapter pipelines as functions (run_ami_anomaly_pipeline, etc.)
- `io.py`: Loaders for CSV, parquet, JSON, GeoJSON
- `eval.py`: Thin wrappers that call metrics from timesmith and anomsmith
- `plots.py`: Thin wrappers that call plotsmith

## Layer 2: API

**Purpose**: Provide a stable public interface. Hide internal module layout.

**Directory**: `src/gridsmith/api/`

**Rules**:
- API exports a small surface
- API validates inputs
- API converts user-friendly config to core contracts

### API Modules

- `client.py`: GridSmithClient with methods that map to book chapters
- `config.py`: Typed configs per chapter (Pydantic models)
- `results.py`: Typed results per chapter

## Layer 3: CLI

**Purpose**: Run every chapter example from the terminal. Make reproducible runs easy.

**Directory**: `src/gridsmith/cli/`

**Rules**:
- CLI calls API only
- CLI accepts a config file path
- CLI writes outputs to a run directory

### CLI Commands

```bash
gridsmith run ami-anomaly --config configs/ami_anomaly.yaml
gridsmith run outage-detect --config configs/outage.yaml
gridsmith validate --config configs/ami_anomaly.yaml
gridsmith info
```

## Layer 4: Examples and Docs

**Purpose**: Tie ML4U chapters to runnable artifacts. Act as product docs and acceptance tests.

**Directories**: `examples/`, `configs/`, `docs/`

**Rules**:
- Each chapter gets one example folder
- Each example folder runs end to end
- Each example folder produces the same artifacts

## Integration Policy

GridSmith depends on Smith libs by version. We:
- Pin minimal versions
- Avoid tight coupling to internal modules
- Import from their public APIs only

## Data Flow

```
User (CLI/API)
  ↓
API Layer (validates, converts config)
  ↓
Core Layer (orchestrates pipelines)
  ↓
Smith Libraries (timesmith, anomsmith, etc.)
  ↓
Results (metrics, tables, figures)
```

## Extension Points

To add a new chapter:
1. Add pipeline function to `core/pipelines.py`
2. Add config class to `api/config.py`
3. Add result class to `api/results.py`
4. Add method to `api/client.py`
5. Add CLI command to `cli/main.py`
6. Create example in `examples/`
7. Add config in `configs/`

