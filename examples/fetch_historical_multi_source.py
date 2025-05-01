#!/usr/bin/env python
"""
Example script demonstrating how to fetch historical data using multiple data sources.
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from psx.core import PSXTicker
from psx.psx_reader import psx_reader
from psx.tradingview import TradingViewClient

def main():
    # Set up parameters
    symbol = "HBL"  # Habib Bank Limited
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 1 year of data
    
    print(f"Fetching historical data for {symbol} from {start_date.date()} to {end_date.date()}")
    
    # 1. Using PSXTicker (tries multiple sources in order)
    print("\n1. Using PSXTicker (tries multiple sources in order):")
    try:
        ticker = PSXTicker(symbol)
        df = ticker.get_historical_data(start_date, end_date)
        print(f"Successfully fetched {len(df)} rows of data")
        print("\nFirst few rows:")
        print(df.head())
    except Exception as e:
        print(f"Error using PSXTicker: {str(e)}")
    
    # 2. Using PSXDataReader directly
    print("\n2. Using PSXDataReader directly:")
    try:
        df = psx_reader.get_historical_data(
            symbol=symbol,
            start_date=start_date.date(),
            end_date=end_date.date()
        )
        print(f"Successfully fetched {len(df)} rows of data")
        print("\nFirst few rows:")
        print(df.head())
    except Exception as e:
        print(f"Error using PSXDataReader: {str(e)}")
    
    # 3. Using TradingView client directly
    print("\n3. Using TradingView client directly:")
    try:
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
            else:
                print("No data returned from TradingView")
        else:
            print(f"Unexpected TradingView response format: {type(tv_data)}")
    except Exception as e:
        print(f"Error using TradingView client: {str(e)}")
    
    # 4. Plot the data if available
    if 'df' in locals() and not df.empty:
        print("\n4. Plotting the data:")
        try:
            plt.figure(figsize=(12, 6))
            plt.plot(df.index, df['Close'], label='Close Price')
            plt.title(f"{symbol} Stock Price")
            plt.xlabel("Date")
            plt.ylabel("Price (PKR)")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"{symbol}_stock_price.png")
            print(f"Plot saved as {symbol}_stock_price.png")
        except Exception as e:
            print(f"Error plotting data: {str(e)}")

if __name__ == "__main__":
    main() 