import logging

def transform(df):
    logging.info("Transforming data...")
    # Vectorized operation: fillna is already vectorized
    df["amount"] = df["amount"].fillna(0)
    # Efficient grouping using pandas optimized groupby
    return df.groupby("region", observed=True)["amount"].sum().reset_index()
