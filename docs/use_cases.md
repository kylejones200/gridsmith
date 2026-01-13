Use Cases
=========

GridSmith solves common problems faced by electric utilities and grid operators. Each pipeline addresses a specific operational challenge.

Asset Risk Assessment
---------------------

**Challenge**: Utilities manage thousands of transformers, cables, and other assets. Traditional maintenance schedules waste money on healthy assets while missing failing ones.

**Solution**: GridSmith's predictive maintenance pipeline analyzes sensor data to identify assets at risk of failure. Outputs include risk scores and prioritized maintenance schedules.

**Example Scenario**:
  A utility monitors 5,000 distribution transformers using SCADA data. GridSmith analyzes temperature, vibration, and load patterns to identify 150 transformers requiring attention. Maintenance crews focus on high-risk assets, reducing unplanned outages by 35% while cutting maintenance costs by 18%.

**Pipelines Used**:
  - predictive-maintenance: Asset health monitoring
  - outage-prediction: Failure risk assessment

Storm Outage Prediction
-----------------------

**Challenge**: Storms cause widespread outages. Utilities struggle to predict which areas will be affected and how to allocate limited crew resources.

**Solution**: GridSmith's outage prediction pipeline uses weather forecasts, asset data, and historical patterns to predict outage locations and severity.

**Example Scenario**:
  A Category 2 hurricane approaches a utility's service territory. GridSmith analyzes wind forecasts, tree density, asset age, and historical outage data. The system predicts 2,500 customers will lose power in specific neighborhoods. The utility pre-positions crews and equipment, reducing average restoration time from 24 hours to 14 hours.

**Pipelines Used**:
  - outage-prediction: Storm outage forecasting
  - geospatial: Spatial risk analysis

Load Forecasting and Planning
------------------------------

**Challenge**: Utilities must balance supply and demand in real-time. Forecasting errors lead to expensive purchases from energy markets or service reliability issues.

**Solution**: GridSmith's load forecasting pipeline combines time series models with weather data to produce accurate demand forecasts.

**Example Scenario**:
  A utility needs hourly load forecasts for the next 7 days for capacity planning. GridSmith analyzes historical consumption, temperature forecasts, and calendar effects. The system produces forecasts with 3% mean absolute error, enabling the utility to optimize generation schedules and reduce market purchases by $2.3M annually.

**Pipelines Used**:
  - load-forecasting: Demand forecasting
  - temperature-load: Weather-load modeling

AMI Anomaly Detection
---------------------

**Challenge**: Advanced metering infrastructure (AMI) generates millions of readings daily. Utilities need to identify meter malfunctions, theft, and unusual consumption patterns automatically.

**Solution**: GridSmith's AMI anomaly detection pipeline processes meter data to identify anomalies requiring investigation.

**Example Scenario**:
  A utility processes 50 million daily meter readings. GridSmith analyzes consumption patterns to identify 2,500 anomalies: 1,200 potential meter failures, 800 possible theft cases, and 500 unusual consumption patterns. Investigation teams prioritize high-confidence cases, reducing investigation time by 65% and recovering $450K annually in lost revenue.

**Pipelines Used**:
  - ami-anomaly: Meter anomaly detection

Capital Planning Optimization
------------------------------

**Challenge**: Utilities must plan multi-year capital investments across thousands of assets. Traditional fixed replacement cycles waste money on healthy assets while risking failures from aging equipment.

**Solution**: GridSmith provides risk-based capital planning by combining asset health scores with cost-benefit analysis.

**Example Scenario**:
  A utility plans a $50M annual capital budget across transformers, cables, and poles. GridSmith generates risk scores for all assets and recommends replacement schedules. The utility shifts $12M from low-risk to high-risk assets, reducing unplanned failures by 28% while maintaining the same budget.

**Pipelines Used**:
  - predictive-maintenance: Asset risk scoring
  - roi-analysis: Cost-benefit analysis

Grid Operations Integration
---------------------------

**Challenge**: Utilities use multiple systems for different analyses. Results are inconsistent, difficult to reproduce, and hard to integrate into operations.

**Solution**: GridSmith provides standardized pipelines that integrate with existing data platforms and produce consistent, reproducible outputs.

**Example Scenario**:
  A utility operates across three regions with different analytical tools. GridSmith standardizes analysis across all regions. Engineers can compare results across regions, reproduce analyses for audits, and integrate outputs into existing operational systems. Regulatory review time decreases by 40% due to consistent, documented results.

**Pipelines Used**:
  - All pipelines provide standardized outputs
  - Integration with existing platforms

Distributed Energy Resource Integration
---------------------------------------

**Challenge**: Growing adoption of solar, batteries, and EVs creates bidirectional power flows. Utilities need to forecast distributed generation and manage grid stability.

**Solution**: GridSmith's DER forecasting pipeline predicts distributed generation and helps plan grid operations.

**Example Scenario**:
  A utility service area has 50,000 residential solar installations and 10,000 EV chargers. GridSmith forecasts distributed generation and EV charging patterns. The utility optimizes voltage regulation, reduces line losses by 8%, and avoids $1.2M in distribution upgrades through better forecasting.

**Pipelines Used**:
  - der-forecasting: Distributed resource forecasting
  - load-forecasting: Net load forecasting

Compliance and Reporting
------------------------

**Challenge**: Utilities must provide detailed analysis to regulators. Traditional scripts are difficult to audit and reproduce.

**Solution**: GridSmith provides versioned, reproducible pipelines with explicit data contracts and documentation.

**Example Scenario**:
  A utility must justify a rate case by demonstrating cost-effective capital planning. GridSmith provides versioned pipelines that show exactly how decisions were made. Regulators can reproduce the analysis, reducing review time and increasing approval confidence.

**Pipelines Used**:
  - All pipelines support audit and compliance
  - Versioned, reproducible results


