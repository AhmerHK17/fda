#!/usr/bin/env python
"""
Test script to verify that our PSX library works like yfinance for HBL.
Tests both today's data and historical data from October 2023 to December 2024.
"""

import sys
import os
from datetime import datetime
import pandas as pd

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from psx.core import PSXDataReader
from psx.tradingview import TradingViewClient

def test_intraday():
    """Test intraday data fetching"""
    print("\nTesting intraday data...")
    reader = PSXDataReader()
    
    for symbol in ["HBL", "PSO"]:
        try:
            data = reader.fetch_intraday_data(symbol)
            print(f"\n{symbol} Intraday Data:")
            print(f"Price: {data['price']}")
            print(f"Change: {data['change_percent']}%")
            print(f"Volume: {data['volume']:,}")
        except Exception as e:
            print(f"Error fetching intraday data for {symbol}: {str(e)}")

def test_historical():
    """Test historical data fetching"""
    print("\nTesting historical data...")
    reader = PSXDataReader()
    
    # Test dates
    start_date = datetime(2023, 10, 1)
    end_date = datetime(2024, 12, 31)
    
    try:
        # Get data using PSXDataReader
        print("\nFetching data using PSXDataReader...")
        df = reader.get_historical_data("HBL", start_date, end_date)
        if df is not None and not df.empty:
            print_data_stats(df, "PSXDataReader")
        else:
            print("No data returned from PSXDataReader")
        
        # Get data using TradingView
        print("\nFetching data using TradingView...")
        tv = TradingViewClient()
        tv_df = tv.get_historical_data("HBL", start_date, end_date)
        if tv_df is not None and not tv_df.empty:
            print_data_stats(tv_df, "TradingView")
        else:
            print("No data returned from TradingView")
        
        # Compare results if both have data
        if df is not None and tv_df is not None and not df.empty and not tv_df.empty:
            print("\nComparing results:")
            print(f"PSXDataReader rows: {len(df)}")
            print(f"TradingView rows: {len(tv_df)}")
        
    except Exception as e:
        print(f"Error in historical data test: {str(e)}")
        import traceback
        traceback.print_exc()

def print_data_stats(df: pd.DataFrame, source: str):
    """Print statistics about the data"""
    try:
        print(f"\n{source} Data Statistics:")
        print(f"Total days: {len(df)}")
        print("\nFirst 5 entries:")
        print(df.head())
        print("\nLast 5 entries:")
        print(df.tail())
        print("\nPrice Statistics:")
        
        # Handle different column name conventions
        close_col = 'Close' if 'Close' in df.columns else 'close'
        high_col = 'High' if 'High' in df.columns else 'high'
        low_col = 'Low' if 'Low' in df.columns else 'low'
        volume_col = 'Volume' if 'Volume' in df.columns else 'volume'
        
        print(f"Average price: {df[close_col].mean():.2f}")
        print(f"Highest price: {df[high_col].max():.2f}")
        print(f"Lowest price: {df[low_col].min():.2f}")
        print(f"Total volume: {df[volume_col].sum():,}")
    except Exception as e:
        print(f"Error printing data stats: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        test_intraday()
        test_historical()
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 