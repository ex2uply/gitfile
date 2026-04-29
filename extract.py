import pandas as pd
import logging

def extract(config, chunk_size=None):
    logging.info("Extracting data...")
    input_file = config["input"]["file"]
    if config["input"]["format"] == "json":
        if chunk_size:
            # Read in chunks for large datasets
            return pd.read_json(input_file, chunksize=chunk_size)
        return pd.read_json(input_file)
    else:
        raise ValueError(f"Unsupported input format: {config['input']['format']}")
