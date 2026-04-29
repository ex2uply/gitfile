import logging
import snowflake.connector

def load_to_snowflake(df, config):
    """
    Load data to Snowflake table.
    Requires snowflake-connector-python package.
    
    Snowflake table creation SQL:
    CREATE TABLE orders_summary (
        region STRING,
        total_revenue FLOAT
    );
    """
    if not config["snowflake"]["enabled"]:
        logging.info("Snowflake integration disabled, skipping...")
        return
    
    logging.info("Loading data to Snowflake...")
    
    conn = snowflake.connector.connect(
        user=config["snowflake"]["user"],
        password=config["snowflake"]["password"],
        account=config["snowflake"]["account"]
    )
    
    cursor = conn.cursor()
    table = config["snowflake"]["table"]

    for _, row in df.iterrows():
        cursor.execute(
            f"INSERT INTO {table} (region, total_revenue) VALUES (%s, %s)",
            (row['region'], row['amount'])
        )

    conn.commit()
    cursor.close()
    conn.close()
    logging.info("Data loaded to Snowflake successfully")
