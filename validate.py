import logging

def validate(df, config):
    logging.info("Validating data...")
    required_cols = config["validation"]["required_columns"]
    
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    # Check for duplicate order_id
    if df["order_id"].duplicated().any():
        duplicates = df[df["order_id"].duplicated()]["order_id"].tolist()
        logging.warning(f"Found duplicate order_ids: {duplicates}")
        df = df.drop_duplicates(subset=["order_id"], keep="first")

    # Check for invalid region values
    valid_regions = config["validation"]["valid_regions"]
    invalid_regions = df[~df["region"].isin(valid_regions)]["region"].unique()
    if len(invalid_regions) > 0:
        logging.warning(f"Found invalid regions: {invalid_regions}")
        df = df[df["region"].isin(valid_regions)]

    # Remove negative amounts
    df = df[df["amount"].isnull() | (df["amount"] >= 0)]
    return df
