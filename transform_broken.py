import logging

def transform(df):
    logging.info("Transforming data...")
    df["amount"] = df["amount"].fillna(0)
    # BUG: Missing .sum() - this will cause an error
    return df.groupby("region")["amount"]
