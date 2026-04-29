import logging
import os
import time

def load(df, config, max_retries=3, retry_delay=1):
    """
    Load data with retry mechanism.
    
    Args:
        df: DataFrame to load
        config: Configuration dictionary
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Delay between retries in seconds (default: 1)
    """
    output_file = config["output"]["file"]
    
    for attempt in range(max_retries):
        try:
            logging.info(f"Loading data (attempt {attempt + 1}/{max_retries})...")
            
            if config["output"]["partition_by_region"]:
                # Partition output by region
                for region in df["region"].unique():
                    region_df = df[df["region"] == region]
                    partition_file = f"output_{region.lower()}.csv"
                    region_df.to_csv(partition_file, index=False)
                    logging.info(f"Saved partition: {partition_file}")
            else:
                # Single output file
                if config["output"]["format"] == "csv":
                    df.to_csv(output_file, index=False)
                else:
                    raise ValueError(f"Unsupported output format: {config['output']['format']}")
            
            logging.info("Data loaded successfully")
            return
            
        except Exception as e:
            if attempt < max_retries - 1:
                logging.warning(f"Load failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logging.error(f"Load failed after {max_retries} attempts: {e}")
                raise
