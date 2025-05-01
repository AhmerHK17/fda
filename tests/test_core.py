import pytest
from psx.core import PSXTicker
import pandas as pd
from datetime import datetime, timedelta

def test_hbl_intraday():
    """Test fetching today's intraday data for HBL"""
    ticker = PSXTicker("HBL")
    df = ticker.intraday()
    
    # Basic DataFrame checks
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    
    # Check required columns exist
    required_columns = ['price', 'volume', 'timestamp']
    for col in required_columns:
        assert col in df.columns
    
    # Check data is from today
    today = pd.Timestamp.now().date()
    assert all(ts.date() == today for ts in df['timestamp'])
    
    # Check data types
    assert pd.api.types.is_numeric_dtype(df['price'])
    assert pd.api.types.is_numeric_dtype(df['volume'])
    
    # Basic value checks
    assert (df['price'] > 0).all()
    assert (df['volume'] >= 0).all()

def test_hbl_historical_oct2023_dec2024():
    """Test fetching historical data for HBL from Oct 2023 to Dec 2024"""
    ticker = PSXTicker("HBL")
    start_date = "2023-10-01"
    end_date = "2024-12-31"
    
    df = ticker.history(start=start_date, end=end_date)
    
    # Basic DataFrame checks
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    
    # Check required columns exist
    required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    for col in required_columns:
        assert col in df.columns
    
    # Convert dates to timestamps for comparison
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    now = pd.Timestamp.now()
    
    # Check date range
    assert df['date'].min() >= start_ts
    assert df['date'].max() <= min(end_ts, now)  # Should not exceed current date
    
    # Check data types
    numeric_columns = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_columns:
        assert pd.api.types.is_numeric_dtype(df[col])
    
    # Basic value checks
    assert (df['high'] >= df['low']).all()
    assert (df['open'] > 0).all()
    assert (df['close'] > 0).all()
    assert (df['volume'] >= 0).all()
    
    # Check for sorted dates
    assert df['date'].is_monotonic_increasing

def test_hbl_historical_invalid_dates():
    """Test handling of invalid date ranges"""
    ticker = PSXTicker("HBL")
    
    # Test future end date
    future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    df = ticker.history(start="2023-10-01", end=future_date)
    assert not df.empty
    assert df['date'].max() <= pd.Timestamp.now()
    
    # Test invalid start date (should raise ValueError)
    with pytest.raises(ValueError):
        ticker.history(start="invalid_date", end="2024-12-31") 