import yaml
import logging
from datetime import datetime

def load_config(config_file="config.yaml"):
    with open(config_file, "r") as f:
        return yaml.safe_load(f)

def setup_logging(config):
    # Structured logging with timestamps and step tracking
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(
        level=config["logging"]["level"],
        format=log_format,
        datefmt=date_format
    )
