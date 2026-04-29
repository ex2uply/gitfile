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
            database=config["snowflake"].get("database", "etl_database"),
            schema=config["snowflake"].get("schema", "etl_schema"),
            warehouse=config["snowflake"].get("warehouse", "COMPUTE_WH")
        )
        
        logging.info(f"Loading {len(df)} rows to Snowflake...")
        
        # Rename columns to match Snowflake table
        df_snowflake = df.rename(columns={"amount": "total_revenue"})
        
        # Use write_pandas for efficient bulk insert
        success, num_chunks, num_rows, _ = write_pandas(
            conn=conn,
            df=df_snowflake,
            table_name=config["snowflake"]["table"],
            database=config["snowflake"].get("database"),
            schema=config["snowflake"].get("schema"),
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
