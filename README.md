# ETL Pipeline with Windsurf + Snowflake

A modular ETL (Extract, Transform, Load) pipeline built with Python, featuring data validation, transformation, and loading capabilities with optional Snowflake integration.

## Features

- **Modular Architecture**: Separate modules for extract, validate, transform, and load operations
- **Data Quality Checks**: Duplicate detection, invalid region validation, negative amount filtering
- **Configuration Management**: YAML-based configuration for easy customization
- **CLI Support**: Command-line interface with argparse
- **Structured Logging**: Timestamped logs with step tracking
- **Retry Mechanism**: Automatic retry on load failures
- **Partitioned Output**: Optional output partitioning by region
- **Optimized for Large Datasets**: Chunk processing and vectorized operations
- **CI/CD Pipeline**: GitHub Actions workflow for automated testing
- **Comprehensive Tests**: Pytest test suite

## Project Structure

```
etl-windsurf-lab/
├── config.py              # Configuration and logging setup
├── extract.py             # Data extraction with chunking support
├── validate.py            # Data validation with quality checks
├── transform.py           # Data transformation
├── load.py                # Data loading with retry mechanism
├── etl.py                 # Main CLI entry point
├── snowflake_loader.py    # Optional Snowflake integration
├── test_etl.py            # Pytest test cases
├── config.yaml            # Configuration file
├── orders.json            # Sample input data
├── requirements.txt       # Python dependencies
└── .github/workflows/ci.yml  # CI/CD pipeline
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ex2uply/gitfile.git
cd gitfile
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the ETL pipeline with default configuration:
```bash
python etl.py
```

### Custom Configuration

Specify a custom configuration file:
```bash
python etl.py --config custom_config.yaml
```

### Configuration

Edit `config.yaml` to customize the pipeline:

```yaml
input:
  file: orders.json
  format: json

output:
  file: snowflake_mock.csv
  format: csv
  partition_by_region: false

validation:
  required_columns:
    - order_id
    - customer_id
    - amount
    - region
  valid_regions:
    - US
    - EU
    - APAC
    - LATAM
    - EMEA

logging:
  level: INFO

snowflake:
  enabled: false
  user: YOUR_USER
  password: YOUR_PASSWORD
  account: YOUR_ACCOUNT
  table: orders_summary
```

## Testing

Run the test suite:
```bash
pytest test_etl.py -v
```

## CI/CD

The project includes a GitHub Actions workflow that automatically:
- Runs tests on push/PR to main and develop branches
- Executes the ETL pipeline
- Verifies output file generation

View workflow status in the "Actions" tab on GitHub.

## Snowflake Integration (Optional)

To enable Snowflake integration:

1. Install the Snowflake connector:
```bash
pip install snowflake-connector-python
```

2. Create the Snowflake table:
```sql
CREATE TABLE orders_summary (
    region STRING,
    total_revenue FLOAT
);
```

3. Update `config.yaml` with your credentials:
```yaml
snowflake:
  enabled: true
  user: YOUR_USER
  password: YOUR_PASSWORD
  account: YOUR_ACCOUNT
  table: orders_summary
```

4. Import and use the Snowflake loader in your pipeline:
```python
from snowflake_loader import load_to_snowflake
load_to_snowflake(df, config)
```

## Data Quality Checks

The pipeline includes the following validations:
- **Required Columns**: Ensures all required columns are present
- **Duplicate Detection**: Identifies and removes duplicate order IDs
- **Region Validation**: Filters out invalid region values
- **Negative Amounts**: Removes rows with negative amounts

## Output

The pipeline generates:
- `snowflake_mock.csv`: Aggregated revenue by region (or partitioned files if enabled)
- Structured logs with timestamps for each step

## Debugging Exercise

A debugging exercise is included in `DEBUGGING_EXERCISE.md` and `transform_broken.py` to practice debugging with AI assistance.

## License

This project is part of the SIG-GENAI-May-2026 training program.
