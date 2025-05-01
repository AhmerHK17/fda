import pytest
from datetime import datetime, date
import pandas as pd
from psx.core import PSXTicker

def test_hbl_intraday():
    """Test fetching intraday data for HBL"""
    ticker = PSXTicker('HBL')
    
    # Get intraday data
    df = ticker.get_intraday_data()
    
    # Print sample data
    print("\nHBL Intraday Data:")
    print(df.head())
    
    # Basic validation
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'price' in df.columns
    assert 'volume' in df.columns
    assert isinstance(df.index, pd.DatetimeIndex)

def test_hbl_historical():
    """Test fetching historical data for HBL from Oct 2022 to Apr 2024"""
    ticker = PSXTicker('HBL')
    
    # Define date range using datetime objects
    start_date = datetime(2022, 10, 1)
    end_date = datetime(2024, 4, 30)
    
    # Get historical data
    df = ticker.get_historical_data(start_date=start_date, end_date=end_date)
    
    # Print data summary
    print("\nHBL Historical Data Summary:")
    print(f"Date Range: {df.index.min()} to {df.index.max()}")
    print(f"Total Trading Days: {len(df)}")
    print("\nFirst 5 entries:")
    print(df.head())
    print("\nLast 5 entries:")
    print(df.tail())
    print("\nPrice Statistics:")
    print(f"Average Close Price: {df['close'].mean():.2f}")
    print(f"Highest Price: {df['high'].max():.2f}")
    print(f"Lowest Price: {df['low'].min():.2f}")
    print(f"Total Volume: {df['volume'].sum():,.0f}")
    
    # Basic validation
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume'])
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.min() >= pd.Timestamp(start_date)
    assert df.index.max() <= pd.Timestamp(end_date) 