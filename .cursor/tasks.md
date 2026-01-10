Paste the text below into Cursor as a single prompt. Use it at the repo root. Keep Cursor on a branch.

Define a new architecture for this time series library. Use four layers. Keep strict boundaries between layers. Create code and tests. Do not move every old module in the first pass. Create the skeleton first. Migrate two representative algorithms end to end as proof.

Create these packages.

Create `timesignal/typing` for scientific types and type checks.
Create `timesignal/core` for base classes, parameter handling, tags, and input validation.
Create `timesignal/compose` for pipeline and adapter objects.
Create `timesignal/tasks` for task objects that bind data, horizon, and target semantics.
Create `timesignal/eval` for split logic, backtests, metrics, and reports.
Create `timesignal/datasets` for loaders and example data only.

Define scientific types as Python protocols plus runtime validators.

Define `SeriesLike` as pandas Series or one column DataFrame with a datetime or integer index.
Define `PanelLike` as DataFrame with an entity key plus time index or a MultiIndex with entity then time.
Define `TableLike` as DataFrame with row index aligned to time or window end times.
Define `ForecastLike` as a small dataclass with `y_pred`, `y_int` optional, `fh`, and metadata.

Add `timesignal/typing/validators.py` with `is_series`, `is_panel`, `is_table`, `assert_series`, `assert_panel`, `assert_table`. Use clear error text.

Create base estimator design in `timesignal/core/base.py`.

Create `BaseObject` with `get_params`, `set_params`, `clone`, and `__repr__`.
Create `BaseEstimator` with `fit` and fitted state.
Create `BaseTransformer` with `transform` and optional `inverse_transform`.
Create `BaseForecaster` with `predict` plus `predict_interval` optional.
Create `BaseDetector` with `score` and `predict` for anomaly flags.
Create `BaseFeaturizer` as a transformer that outputs `TableLike`.

Add a small tag system in `timesignal/core/tags.py`. Use dict tags on each class. Add tags like `scitype_input`, `scitype_output`, `handles_missing`, `requires_sorted_index`, `supports_panel`, `requires_fh`.

Add strict input checks in `timesignal/core/validate.py`. Validate once at public API boundaries only. Do not validate inside inner loops.

Create composition in `timesignal/compose`.

Create `Pipeline` that chains steps. Support scitype change across steps.
Create `Adapter` objects that convert scitypes. Example. Series to Table via window features. Table to Series via aligned join.
Create `FeatureUnion` that runs multiple featurizers then concatenates tables.
Create `ForecasterPipeline` that supports transformer then forecaster.
Expose `make_pipeline` and `make_forecaster_pipeline`.

Create tasks in `timesignal/tasks`.

Create `ForecastTask`. Include `y`, optional `X`, `fh`, `cutoff`, `frequency` optional.
Create `DetectTask`. Include `y`, optional `X`, optional labels, horizon optional.
Tasks hold semantics. Estimators do not store global config beyond params and fitted state.

Create evaluation in `timesignal/eval`.

Create splitters. `ExpandingWindowSplit` and `SlidingWindowSplit`.
Create metrics. `mae`, `rmse`, `mape` with safe zero handling.
Create backtest. `backtest_forecaster` that accepts a forecaster or forecaster pipeline and a task, then returns a results table with fold id, cutoff, fh, y_true, y_pred, metrics.
Create report. `summarize_backtest` that returns aggregate metrics plus per fold metrics.

Create docs and examples.

Create `README.md` section that shows the four layers and one end to end example.
Create `examples/` with one script that loads a built in dataset, builds a pipeline, runs backtest, prints summary.

Migrate two real modules from the existing repo as proof.

Pick one transformer you already have. Wrap it as `BaseTransformer`.
Pick one forecaster you already have. Wrap it as `BaseForecaster`.
Make them pass through the new pipeline and backtest path.

Write tests first for the new skeleton.

Add unit tests for validators.
Add unit tests for parameter round trip on base objects.
Add unit tests for pipeline scitype change with adapters.
Add unit tests for expanding split logic.
Add unit tests for backtest output schema.

Add style rules for the repo.

Use logging. No print in library code.
Keep imports minimal.
Keep public API in `timesignal/__init__.py` and do not leak internal modules.
Use Google docstrings.
Add type hints.
Add `pyproject.toml` updates if needed.

Define acceptance criteria.

A user can run `python examples/basic_forecast.py` and get a results table plus a summary.
All tests pass.
The old code stays in place. Only the two migrated components route through the new architecture.


Structure for Timesmith.

Create timesmith/typing for scitypes and validators.
Create timesmith/core for BaseObject, BaseEstimator, tags, and config.
Create timesmith/compose for Pipeline, adapters, unions.
Create timesmith/tasks for ForecastTask and DetectTask.
Create timesmith/eval for splitters, metrics, backtests, summaries.
Create timesmith/results for Forecast and BacktestResult dataclasses.
Create timesmith/utils for small helpers only.

Then enforce boundaries. Core cannot import eval. Typing cannot import anything. Domain packages can import from Timesmith but Timesmith cannot import from domain packages.