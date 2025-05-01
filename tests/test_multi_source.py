#!/usr/bin/env python
"""
Test script to verify that the multi-source implementation works.
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from psx.core import PSXTicker
from psx.psx_reader import psx_reader
from psx.tradingview import TradingViewClient

def test_psx_ticker():
    """Test the PSXTicker class with multiple data sources."""
    print("\n=== Testing PSXTicker with multiple data sources ===")
    
    # Set up parameters
    symbol = "HBL"  # Habib Bank Limited
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # 30 days of data
    
    print(f"Fetching historical data for {symbol} from {start_date.date()} to {end_date.date()}")
    
    try:
        # Create a PSXTicker instance
        ticker = PSXTicker(symbol)
        
        # Try with all data sources
        print("\n1. Trying with all data sources:")
        df = ticker.get_historical_data(start_date, end_date)
        print(f"Successfully fetched {len(df)} rows of data")
        print("\nFirst few rows:")
        print(df.head())
        
        # Try with only PSX API and TradingView
        print("\n2. Trying with only PSX API and TradingView:")
        df = ticker.get_historical_data(
            start_date, 
            end_date, 
            use_tradingview=True, 
            use_psx_reader=False
        )
        print(f"Successfully fetched {len(df)} rows of data")
        
        # Try with only PSX API
        print("\n3. Trying with only PSX API:")
        df = ticker.get_historical_data(
            start_date, 
            end_date, 
            use_tradingview=False, 
            use_psx_reader=False
        )
        print(f"Successfully fetched {len(df)} rows of data")
        
        return True
    except Exception as e:
        print(f"Error testing PSXTicker: {str(e)}")
        return False

def test_psx_reader():
    """Test the PSXDataReader class directly."""
    print("\n=== Testing PSXDataReader directly ===")
    
    # Set up parameters
    symbol = "HBL"  # Habib Bank Limited
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # 30 days of data
    
    print(f"Fetching historical data for {symbol} from {start_date.date()} to {end_date.date()}")
    
    try:
        # Use the PSXDataReader directly
        df = psx_reader.get_historical_data(
            symbol=symbol,
            start_date=start_date.date(),
            end_date=end_date.date()
        )
        print(f"Successfully fetched {len(df)} rows of data")
        print("\nFirst few rows:")
        print(df.head())
        
        return True
    except Exception as e:
        print(f"Error testing PSXDataReader: {str(e)}")
        return False

def test_tradingview():
    """Test the TradingView client directly."""
    print("\n=== Testing TradingView client directly ===")
    
    # Set up parameters
    symbol = "HBL"  # Habib Bank Limited
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # 30 days of data
    
    print(f"Fetching historical data for {symbol} from {start_date.date()} to {end_date.date()}")
    
    try:
        # Use the TradingView client directly
        tv_client = TradingViewClient()
        tv_data = tv_client.get_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        # Convert TradingView data to DataFrame
        if isinstance(tv_data, dict) and 'data' in tv_data:
            data = []
            for entry in tv_data['data']:
                if isinstance(entry, list) and len(entry) >= 6:
                    date_str, open_val, high, low, close, volume = entry
                    data.append({
                        'date': pd.to_datetime(date_str),
                        'open': open_val,
                        'high': high,
                        'low': low,
                        'close': close,
                        'volume': volume
                    })
            
            df = pd.DataFrame(data)
            if not df.empty:
                df.set_index('date', inplace=True)
                print(f"Successfully fetched {len(df)} rows of data")
                print("\nFirst few rows:")
                print(df.head())
                return True
            else:
                print("No data returned from TradingView")
                return False
        else:
            print(f"Unexpected TradingView response format: {type(tv_data)}")
            return False
    except Exception as e:
        print(f"Error testing TradingView client: {str(e)}")
        return False

def main():
    """Run all tests."""
    results = {
        "PSXTicker": test_psx_ticker(),
        "PSXDataReader": test_psx_reader(),
        "TradingView": test_tradingview()
    }
    
    print("\n=== Test Results ===")
    for test, passed in results.items():
        print(f"{test}: {'PASSED' if passed else 'FAILED'}")
    
    # Overall result
    if all(results.values()):
        print("\nAll tests PASSED!")
        return 0
    else:
        print("\nSome tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 