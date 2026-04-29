import os
import yaml
from dotenv import load_dotenv

def load_secure_config(config_file="config.yaml"):
    """Load configuration with environment variable overrides for security."""
    # Load .env file if it exists
    load_dotenv()
    
    # Load YAML config
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    # Override with environment variables for Snowflake credentials
    if "snowflake" in config:
        config["snowflake"]["account"] = os.getenv("SNOWFLAKE_ACCOUNT", config["snowflake"].get("account", ""))
        config["snowflake"]["user"] = os.getenv("SNOWFLAKE_USER", config["snowflake"].get("user", ""))
        config["snowflake"]["password"] = os.getenv("SNOWFLAKE_PASSWORD", config["snowflake"].get("password", ""))
        config["snowflake"]["database"] = os.getenv("SNOWFLAKE_DATABASE", config["snowflake"].get("database", "etl_database"))
        config["snowflake"]["schema"] = os.getenv("SNOWFLAKE_SCHEMA", config["snowflake"].get("schema", "etl_schema"))
        config["snowflake"]["warehouse"] = os.getenv("SNOWFLAKE_WAREHOUSE", config["snowflake"].get("warehouse", "COMPUTE_WH"))
        config["snowflake"]["table"] = os.getenv("SNOWFLAKE_TABLE", config["snowflake"].get("table", "orders_summary"))
        
        # Parse enabled from string or boolean
        enabled_val = os.getenv("SNOWFLAKE_ENABLED", str(config["snowflake"].get("enabled", False)))
        config["snowflake"]["enabled"] = enabled_val.lower() in ("true", "1", "yes", "on")
    
    return config
