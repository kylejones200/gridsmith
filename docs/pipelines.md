Available Pipelines
===================

GridSmith provides machine learning pipelines for utility operations. Each pipeline solves a specific grid operations problem with standardized inputs and outputs.

All pipelines accept YAML configuration files and produce:
  - Metrics in JSON format
  - Results tables in Parquet format
  - Visualizations as PNG figures
  - Audit-ready documentation

Here are the key pipelines:

Core Applications
-----------------

- **ami-anomaly**: AMI anomaly detection
- **temperature-load**: Temperature-to-load modeling
- **load-forecasting**: Load forecasting with ARIMA/LSTM
- **predictive-maintenance**: Asset health monitoring
- **outage-prediction**: Storm outage prediction
- **grid-optimization**: Grid optimization with RL
- **der-forecasting**: Distributed energy resource forecasting
- **demand-response**: Customer load profiling

Advanced Techniques
-------------------

- **computer-vision**: Vegetation detection
- **nlp**: Log classification
- **ai-utilities**: LLM integration
- **geospatial**: Feeder mapping, asset location

Integration & Scale
-------------------

- **mlops**: MLflow integration
- **cybersecurity**: Threat detection
- **ethics**: Fairness auditing
- **roi-analysis**: Cost-benefit analysis
- **realtime-analytics**: Streaming analytics
- **compliance**: SAIDI/SAIFI reporting
- **feature-engineering**: Temporal, geospatial features
- **reliability**: Reliability analytics
- **market-operations**: Price forecasting, bidding

Advanced Research
-----------------

- **causal-inference**: Causal methods
- **multi-task-learning**: MTL models

Pipeline Outputs
----------------

Every GridSmith pipeline produces consistent outputs:

**Metrics** (`metrics.json`)
  Quantitative measures of model performance, system health, or operational indicators.

**Tables** (`tables/*.parquet`)
  Detailed results in Parquet format, suitable for further analysis or integration with data platforms.

**Figures** (`figures/*.png`)
  Visualizations showing trends, predictions, anomalies, or relationships.

**Logs** (`logs/*.log`)
  Execution logs for debugging and audit trails.

Integration
-----------

Pipelines integrate with existing utility data platforms. Input data comes from CSV or Parquet files. Outputs are structured for easy integration with:
  - Data warehouses and lakes
  - Operational dashboards
  - Regulatory reporting systems
  - GIS platforms

See :doc:`how_to_run` for detailed usage instructions and :doc:`use_cases` for real-world scenarios.

