# Smith Library Integration Analysis

## Available APIs

### plotsmith (0.2.0)
- `plot_timeseries(data, bands=None, title=None, xlabel=None, ylabel=None, save_path=None, figsize=(10, 6))`
  - Returns: `(fig, ax)` tuple
  - Note: Function name is `plot_timeseries` (not `plot_time_series`)
  
- `plot_forecast_comparison(actual, forecasts, intervals=None, title=None, xlabel=None, ylabel=None, save_path=None, figsize=(12, 6))`
  - Returns: `(fig, ax)` tuple
  - Takes dict of forecasts for comparison

- `plot_backtest` - for backtest visualization

### timesmith (0.1.2)
- **Metrics**:
  - `mae(y_true, y_pred) -> float`
  - `rmse(y_true, y_pred) -> float`
  - `mape(y_true, y_pred) -> float`
  
- **Plotting**:
  - `plot_forecast(historical, forecast, intervals=None, title='Forecast', **kwargs)`
  - `plot_timeseries` - exists
  
- **Forecasters**:
  - `ARIMAForecaster`, `ExponentialSmoothingForecaster`, `LSTMForecaster`, etc.
  - `backtest_forecaster` - for backtesting

## Simplification Opportunities

### 1. plots.py - Simplify plotsmith calls

**Current**: Complex fallback logic with multiple API pattern checks
**Can simplify to**: Direct API calls since we know the actual API

Issues to fix:
- Function name mismatch: code looks for `plot_time_series` but API has `plot_timeseries`
- Complex hasattr() checks that can be removed
- Complex save logic that can use `save_path` parameter directly

### 2. eval.py - Use timesmith metrics directly

**Current**: Complex fallback logic trying multiple API patterns
**Can simplify to**: Direct calls to `timesmith.mae`, `timesmith.rmse`, `timesmith.mape`

Benefits:
- Remove 50+ lines of complex fallback code
- Use actual timesmith functions directly
- Cleaner, more maintainable code

### 3. pipelines.py - Use timesmith forecasters directly

**Current**: Complex API pattern matching with multiple fallbacks
**Can simplify to**: Use timesmith forecasters directly (e.g., `ARIMAForecaster`, `ExponentialSmoothingForecaster`)

Benefits:
- Remove 100+ lines of complex integration code
- Use standard timesmith API
- Better error handling

