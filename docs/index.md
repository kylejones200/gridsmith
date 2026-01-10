GridSmith
=========

GridSmith is a machine learning foundation for electric grid operations.
It provides structured, reproducible pipelines for utility analytics.
It focuses on operational use, not experimentation.

GridSmith composes Smith libraries into complete systems.
Each system solves a common grid problem end to end.
GridSmith emphasizes contracts, repeatability, and auditability.

Audience
--------

GridSmith serves electric utilities and grid operators.
It supports transmission, distribution, and asset management teams.

Problem Space
-------------

Electric grids generate high volume time series, spatial, and event data.
Utilities face aging assets, weather driven risk, and regulatory pressure.
One off models and dashboards fail to scale across the grid.

GridSmith addresses this gap.

Capabilities
------------

GridSmith supports key utility operations:

**Anomaly Detection**
  Identify meter malfunctions, theft, and unusual consumption patterns automatically.

**Asset Risk Scoring**
  Prioritize maintenance and replacement based on quantified failure risk.

**Degradation Analysis**
  Detect equipment degradation before failures occur.

**Outage Analysis**
  Predict storm-related outages and optimize crew allocation.

**Forecasting**
  Forecast load, generation, and distributed energy resources.

**Spatial Risk**
  Analyze geographic patterns and optimize grid operations.

GridSmith integrates time series, networks, geometry, and optimization in a single framework.

Architecture
------------

GridSmith orchestrates TimeSmith, AnomSmith, GeoSmith, ResSmith, and PlotSmith.
Each library owns its domain.
GridSmith binds them into operational pipelines.

How GridSmith Is Used
---------------------

GridSmith runs as code.
Teams execute pipelines from the CLI or Python.
Outputs include metrics, tables, and figures suitable for operations and reporting.

GridSmith does not require a dashboard or service layer.
It integrates with existing data platforms.

Quick Start
-----------

Install GridSmith:

.. code-block:: bash

   pip install gridsmith

Run your first pipeline:

.. code-block:: bash

   gridsmith run ami-anomaly --config configs/ami_anomaly.yaml

Results are saved to timestamped directories with metrics, tables, and figures ready for operations teams.

See :doc:`how_to_run` for detailed usage instructions.

Contents
--------

.. toctree::
   :maxdepth: 2

   overview
   use_cases
   architecture
   data
   pipelines
   how_to_run
   integration
   faq
