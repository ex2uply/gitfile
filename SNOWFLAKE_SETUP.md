# Snowflake Configuration Guide

## Overview

This guide covers proper Snowflake configuration for production use with environment variables and secure credential management.

## Security Best Practices

**Never commit credentials to Git!** Use environment variables instead.

## Step 1: Create Snowflake Account & Resources

### 1.1 Create Database and Schema
```sql
-- Connect to Snowflake as ACCOUNTADMIN or SYSADMIN
CREATE DATABASE IF NOT EXISTS etl_database;
USE DATABASE etl_database;

CREATE SCHEMA IF NOT EXISTS etl_schema;
USE SCHEMA etl_schema;
```

### 1.2 Create Target Table
```sql
CREATE TABLE IF NOT EXISTS orders_summary (
    region STRING,
    total_revenue FLOAT,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 1.3 Create ETL User (Recommended)
```sql
-- Create a dedicated user for ETL operations
CREATE USER IF NOT EXISTS etl_user
    PASSWORD = 'YourStrongPassword123!'
    DEFAULT_ROLE = etl_role
    MUST_CHANGE_PASSWORD = FALSE;

-- Create role with appropriate permissions
CREATE ROLE IF NOT EXISTS etl_role;

-- Grant privileges
GRANT USAGE ON DATABASE etl_database TO ROLE etl_role;
GRANT USAGE ON SCHEMA etl_database.etl_schema TO ROLE etl_role;
GRANT INSERT, SELECT ON TABLE etl_database.etl_schema.orders_summary TO ROLE etl_role;

-- Assign role to user
GRANT ROLE etl_role TO USER etl_user;
```

## Step 2: Configure Environment Variables

### 2.1 Create .env file (add to .gitignore!)

Create `.env` file in project root:
```bash
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=etl_user
SNOWFLAKE_PASSWORD=YourStrongPassword123!
SNOWFLAKE_DATABASE=etl_database
SNOWFLAKE_SCHEMA=etl_schema
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_TABLE=orders_summary
SNOWFLAKE_ENABLED=true
```

### 2.2 Add .env to .gitignore
```bash
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore for security"
```

## Step 3: Update Configuration Files

### 3.1 Update config.yaml
Remove hardcoded credentials, use environment variables:

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
  enabled: true  # Set to false to use mock CSV output
  # Credentials loaded from environment variables
  # See .env file for configuration
```

### 3.2 Install python-dotenv
```bash
pip install python-dotenv
```

Add to requirements.txt:
```
python-dotenv>=1.0.0
```

### 3.3 Create config_loader.py
Create a new file for secure configuration loading:

```python
import os
import yaml
from dotenv import load_dotenv

def load_secure_config(config_file="config.yaml"):
    """Load configuration with environment variable overrides."""
    # Load .env file if it exists
    load_dotenv()
    
    # Load YAML config
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    # Override with environment variables for security
    config["snowflake"]["account"] = os.getenv("SNOWFLAKE_ACCOUNT", "")
    config["snowflake"]["user"] = os.getenv("SNOWFLAKE_USER", "")
    config["snowflake"]["password"] = os.getenv("SNOWFLAKE_PASSWORD", "")
    config["snowflake"]["database"] = os.getenv("SNOWFLAKE_DATABASE", "etl_database")
    config["snowflake"]["schema"] = os.getenv("SNOWFLAKE_SCHEMA", "etl_schema")
    config["snowflake"]["warehouse"] = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
    config["snowflake"]["table"] = os.getenv("SNOWFLAKE_TABLE", "orders_summary")
    config["snowflake"]["enabled"] = os.getenv("SNOWFLAKE_ENABLED", "false").lower() == "true"
    
    return config
```

## Step 4: Update snowflake_loader.py

Replace the existing loader with this secure version:

```python
import logging
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

def load_to_snowflake(df, config):
    """
    Load data to Snowflake table securely.
    
    Args:
        df: pandas DataFrame with columns: region, amount
        config: configuration dictionary with snowflake settings
    """
    if not config["snowflake"]["enabled"]:
        logging.info("Snowflake integration disabled, using mock CSV output...")
        return False
    
    # Check if credentials are set
    required_fields = ["account", "user", "password"]
    for field in required_fields:
        if not config["snowflake"].get(field):
            logging.error(f"Missing Snowflake credential: {field}")
            return False
    
    conn = None
    try:
        logging.info("Connecting to Snowflake...")
        
        conn = snowflake.connector.connect(
            account=config["snowflake"]["account"],
            user=config["snowflake"]["user"],
            password=config["snowflake"]["password"],
            database=config["snowflake"]["database"],
            schema=config["snowflake"]["schema"],
            warehouse=config["snowflake"]["warehouse"]
        )
        
        logging.info(f"Loading {len(df)} rows to Snowflake...")
        
        # Rename columns to match Snowflake table
        df_snowflake = df.rename(columns={"amount": "total_revenue"})
        
        # Use write_pandas for efficient bulk insert
        success, num_chunks, num_rows, _ = write_pandas(
            conn=conn,
            df=df_snowflake,
            table_name=config["snowflake"]["table"],
            database=config["snowflake"]["database"],
            schema=config["snowflake"]["schema"],
            auto_create_table=False
        )
        
        if success:
            logging.info(f"Successfully loaded {num_rows} rows to Snowflake in {num_chunks} chunks")
            return True
        else:
            logging.error("Failed to load data to Snowflake")
            return False
            
    except Exception as e:
        logging.error(f"Snowflake load failed: {e}")
        return False
    finally:
        if conn:
            conn.close()
            logging.info("Snowflake connection closed")
```

## Step 5: Update etl.py to Use Secure Config

```python
import logging
import argparse
from config_loader import load_secure_config
from config import setup_logging
from extract import extract
from validate import validate
from transform import transform
from snowflake_loader import load_to_snowflake
from load import load as mock_load

def run(config_file="config.yaml"):
    config = load_secure_config(config_file)
    setup_logging(config)
    
    try:
        # Extract
        df = extract(config)
        logging.info(f"Extracted {len(df)} rows")
        
        # Validate
        df = validate(df, config)
        logging.info(f"Validated: {len(df)} rows remaining")
        
        # Transform
        df = transform(df)
        logging.info(f"Transformed into {len(df)} aggregated rows")
        
        # Load
        if config["snowflake"]["enabled"]:
            success = load_to_snowflake(df, config)
            if not success:
                logging.warning("Snowflake load failed, falling back to mock CSV")
                mock_load(df, config)
        else:
            mock_load(df, config)
        
        logging.info("ETL completed successfully")
        return True
        
    except Exception as e:
        logging.error(f"ETL failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="ETL Pipeline for processing orders data")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--use-snowflake", action="store_true", help="Force Snowflake mode")
    args = parser.parse_args()
    
    success = run(args.config)
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

## Step 6: Update requirements.txt

```
pandas>=2.0.0
pyyaml>=6.0
pytest>=9.0.0
python-dotenv>=1.0.0
snowflake-connector-python>=3.0.0
```

## Step 7: Running with Snowflake

### 7.1 Set Environment Variables (Command Line)
```bash
export SNOWFLAKE_ACCOUNT="your_account"
export SNOWFLAKE_USER="etl_user"
export SNOWFLAKE_PASSWORD="your_password"
export SNOWFLAKE_ENABLED="true"

python etl.py
```

### 7.2 Or Use .env File
```bash
# Just run - credentials loaded from .env
python etl.py
```

## Step 8: CI/CD with Snowflake (GitHub Actions Secrets)

For CI/CD, use GitHub Secrets:

1. Go to GitHub Repo → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `SNOWFLAKE_ACCOUNT`
   - `SNOWFLAKE_USER`
   - `SNOWFLAKE_PASSWORD`
   - `SNOWFLAKE_DATABASE`
   - `SNOWFLAKE_SCHEMA`

3. Update `.github/workflows/ci.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - uses: actions/setup-python@v5
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: pytest test_etl.py -v
      env:
        SNOWFLAKE_ENABLED: "false"  # Disable for tests
    
    - name: Run ETL (Mock Mode)
      run: python etl.py
      env:
        SNOWFLAKE_ENABLED: "false"
  
  # Optional: Deploy job with Snowflake
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Run ETL to Snowflake
      run: python etl.py --use-snowflake
      env:
        SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
        SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
        SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
        SNOWFLAKE_DATABASE: ${{ secrets.SNOWFLAKE_DATABASE }}
        SNOWFLAKE_SCHEMA: ${{ secrets.SNOWFLAKE_SCHEMA }}
        SNOWFLAKE_ENABLED: "true"
```

## Troubleshooting

### Connection Issues
```bash
# Test Snowflake connection
python -c "
import snowflake.connector
conn = snowflake.connector.connect(
    account='your_account',
    user='your_user',
    password='your_password'
)
print('Connected successfully!')
conn.close()
"
```

### Common Errors
- **Invalid account identifier**: Use format `xy12345` or `xy12345.us-east-1`
- **Authentication failed**: Check username/password
- **Database/Schema not found**: Verify they exist in Snowflake
- **Permission denied**: Grant INSERT/SELECT privileges to the user

## Verification

After successful load, verify data in Snowflake:
```sql
SELECT * FROM orders_summary ORDER BY load_timestamp DESC LIMIT 10;
```
