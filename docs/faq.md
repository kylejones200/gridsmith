Frequently Asked Questions
==========================

Common questions about GridSmith for utilities and grid operators.

What is GridSmith?
------------------

GridSmith is a machine learning foundation for electric grid operations. It provides structured, reproducible pipelines for utility analytics. GridSmith focuses on operational use, not experimentation.

Who uses GridSmith?
-------------------

GridSmith serves electric utilities and grid operators. It supports transmission, distribution, and asset management teams. Engineering, operations, and planning departments all benefit from standardized pipelines.

What problems does GridSmith solve?
------------------------------------

GridSmith addresses common utility challenges:
  - Fragmented analytical tooling
  - Inconsistent results across regions
  - Difficulty reproducing analyses
  - Regulatory compliance challenges
  - Capital planning optimization
  - Operational risk management

How is GridSmith different from other analytics tools?
-------------------------------------------------------

GridSmith provides standardized pipelines with explicit data contracts. Unlike one-off scripts or dashboards, GridSmith ensures:
  - Consistent outputs across regions
  - Reproducible results
  - Audit-ready documentation
  - Versioned pipelines
  - Integration with existing data platforms

Does GridSmith require a dashboard or service layer?
-----------------------------------------------------

No. GridSmith runs as code. Teams execute pipelines from the CLI or Python. Outputs include metrics, tables, and figures suitable for operations and reporting. GridSmith integrates with existing data platforms rather than requiring new infrastructure.

What data formats does GridSmith support?
------------------------------------------

GridSmith supports CSV and Parquet input files. Outputs are standardized: metrics in JSON, tables in Parquet, figures as PNG. This ensures compatibility with existing utility data platforms.

How long does it take to implement GridSmith?
----------------------------------------------

GridSmith integrates with existing data platforms. Typical implementation time:
  - Initial setup: 1-2 days
  - First pipeline: 2-4 hours
  - Full deployment: 2-4 weeks (depending on data integration)

GridSmith does not require new infrastructure or data warehouses.

Does GridSmith require specialized ML expertise?
------------------------------------------------

No. GridSmith provides standardized pipelines that work out of the box. Teams configure pipelines via YAML files. No machine learning expertise required for routine operations. Advanced users can customize pipelines through configuration.

Can GridSmith run on-premises?
-------------------------------

Yes. GridSmith runs anywhere Python runs. It supports cloud and on-premises deployments. GridSmith integrates with existing utility environments without requiring new infrastructure.

How does GridSmith handle regulatory compliance?
-------------------------------------------------

GridSmith supports regulatory compliance through:
  - Versioned pipelines that document decision-making
  - Reproducible results for audits
  - Explicit data contracts that prevent silent failures
  - Documentation suitable for regulatory review

How does GridSmith integrate with existing systems?
----------------------------------------------------

GridSmith integrates with existing data platforms:
  - Reads from CSV and Parquet files (common in utilities)
  - Outputs standard formats (JSON, Parquet, PNG)
  - Works with existing data warehouses and lakes
  - Integrates with operational dashboards
  - Supports GIS platforms

What is the difference between GridSmith and Smith libraries?
--------------------------------------------------------------

Smith libraries (TimeSmith, AnomSmith, GeoSmith, ResSmith, PlotSmith) provide domain-specific algorithms. GridSmith orchestrates these libraries into complete operational pipelines. GridSmith focuses on orchestration and contracts, not algorithm development.

How much does GridSmith cost?
------------------------------

GridSmith is open source and free to use. It integrates with existing utility infrastructure, reducing the need for expensive proprietary platforms.

What support is available?
---------------------------

GridSmith is open source software. Community support is available through GitHub issues and discussions. Commercial support may be available from vendors.

How do I get started?
---------------------

1. Install GridSmith: ``pip install gridsmith``
2. Review the use cases to identify relevant pipelines
3. Prepare your data in CSV or Parquet format
4. Run your first pipeline using the CLI or Python API
5. Review outputs and integrate into operations

See :doc:`how_to_run` for detailed instructions.


