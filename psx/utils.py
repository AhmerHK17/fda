import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

def parse_timeseries_data(data: List[List[Any]]) -> pd.DataFrame:
    """
    Parse the timeseries data from PSX API into a pandas DataFrame.
    
    Args:
        data: List of lists containing [timestamp, price, volume]
        
    Returns:
        pandas DataFrame with columns [timestamp, price, volume]
    """
    df = pd.DataFrame(data, columns=['timestamp', 'price', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    return df.sort_values('timestamp')

def process_historical_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process historical data into OHLCV format.
    
    Args:
        df: DataFrame with timestamp, price, volume columns
        
    Returns:
        DataFrame with date, open, high, low, close, volume columns
    """
    # Convert timestamp to date
    df['date'] = df['timestamp'].dt.date
    
    # Group by date and calculate OHLCV
    daily = df.groupby('date').agg({
        'price': ['first', 'max', 'min', 'last'],
        'volume': 'sum'
    }).reset_index()
    
    # Rename columns
    daily.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    
    # Convert date back to datetime
    daily['date'] = pd.to_datetime(daily['date'])
    
    return daily.sort_values('date')

def validate_symbol(symbol: str) -> str:
    """
    Validate and format the stock symbol.
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        Formatted symbol string
    """
    if not isinstance(symbol, str):
        raise ValueError("Symbol must be a string")
    
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty")
    
    return symbol 