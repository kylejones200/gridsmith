# Sample Data Directory

Place your AMI data CSV or Parquet file here.

## Expected Format

The data should have the following columns:
- `timestamp`: Timestamp of measurement (ISO format or parseable datetime)
- `consumption`: Energy consumption value (numeric)
- `meter_id` (optional): Meter identifier

## Example CSV Format

```csv
timestamp,consumption,meter_id
2024-01-01 00:00:00,100.5,meter_001
2024-01-01 01:00:00,102.3,meter_001
2024-01-01 02:00:00,99.8,meter_001
...
```

## Generating Sample Data

You can generate sample data for testing using:

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate sample data
start_time = datetime(2024, 1, 1)
timestamps = [start_time + timedelta(hours=i) for i in range(100)]
np.random.seed(42)
consumption = 100 + np.random.normal(0, 10, 100)

# Add some anomalies
consumption[20] = 200
consumption[50] = 250
consumption[75] = 50

df = pd.DataFrame({
    "timestamp": timestamps,
    "consumption": consumption,
    "meter_id": ["meter_001"] * 100,
})

df.to_csv("ami_data.csv", index=False)
```

