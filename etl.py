import logging
import argparse
from config import load_config, setup_logging
from extract import extract
from validate import validate
from transform import transform
from load import load

def run(config_file="config.yaml"):
    config = load_config(config_file)
    setup_logging(config)
    
    try:
        df = extract(config)
        df = validate(df, config)
        df = transform(df)
        load(df, config)
        logging.info("ETL completed successfully")
    except Exception as e:
        logging.error(f"ETL failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="ETL Pipeline for processing orders data")
    parser.add_argument("--config", default="config.yaml", help="Path to config file (default: config.yaml)")
    args = parser.parse_args()
    run(args.config)

if __name__ == "__main__":
    main()
