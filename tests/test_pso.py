import pytest
from datetime import datetime
import pandas as pd
from psx.core import PSXTicker
from psx.exceptions import PSXRequestError

def test_get_intraday_data():
    """Test fetching intraday data for PSO"""
    ticker = PSXTicker('PSO')
    
    # Get intraday data
    df = ticker.get_intraday_data()
    
    # Verify DataFrame structure
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'price' in df.columns
    assert 'volume' in df.columns
    assert isinstance(df.index, pd.DatetimeIndex)
    
    # Verify data types
    assert pd.api.types.is_numeric_dtype(df['price'])
    assert pd.api.types.is_numeric_dtype(df['volume'])
    
    # Verify timestamps are recent
    latest_timestamp = df.index.max()
    assert (datetime.now() - latest_timestamp).total_seconds() < 3600  # Within last hour
    
    # Print sample data
    print("\nSample intraday data:")
    print(df.head())

def test_invalid_symbol():
    """Test handling of invalid symbol"""
    ticker = PSXTicker('INVALID')
    
    with pytest.raises(PSXRequestError):
        ticker.get_intraday_data() 