import pytest
import pandas as pd
from transform import transform

def test_transform_null_replacement():
    """Test that null amounts are replaced with 0"""
    df = pd.DataFrame({
        "region": ["US", "EU"],
        "amount": [100, None]
    })
    result = transform(df)
    assert result["amount"].isnull().sum() == 0
    # After aggregation, EU should have 0 (null replaced with 0)
    eu_row = result[result["region"] == "EU"].iloc[0]
    assert eu_row["amount"] == 0

def test_transform_aggregation():
    """Test that amounts are aggregated by region"""
    df = pd.DataFrame({
        "region": ["US", "US", "EU"],
        "amount": [100, 50, 200]
    })
    result = transform(df)
    assert len(result) == 2
    us_row = result[result["region"] == "US"].iloc[0]
    assert us_row["amount"] == 150

def test_transform_returns_dataframe():
    """Test that transform returns a DataFrame"""
    df = pd.DataFrame({
        "region": ["US"],
        "amount": [100]
    })
    result = transform(df)
    assert isinstance(result, pd.DataFrame)
    assert "region" in result.columns
    assert "amount" in result.columns

def test_transform_empty_dataframe():
    """Test transform with empty DataFrame"""
    df = pd.DataFrame({
        "region": [],
        "amount": []
    })
    result = transform(df)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0
