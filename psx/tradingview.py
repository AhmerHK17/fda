from tvDatafeed import TvDatafeed, Interval
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from .exceptions import PSXError, PSXConnectionError, PSXDataError
import pandas as pd

class TradingViewClient:
    """Client for interacting with TradingView data"""
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize TradingView client.
        
        Args:
            username: TradingView username (optional)
            password: TradingView password (optional)
        """
        try:
            self.tv = TvDatafeed(username=username, password=password)
        except Exception as e:
            raise PSXConnectionError(f"Failed to initialize TradingView client: {str(e)}")
            
    def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Get historical data for a symbol between start_date and end_date
        
        Parameters
        ----------
        symbol : str
            Symbol to get data for
        start_date : datetime
            Start date for historical data
        end_date : datetime
            End date for historical data
            
        Returns
        -------
        pd.DataFrame
            DataFrame with historical data
        """
        try:
            # Convert dates to timestamps
            from_time = int(start_date.timestamp())
            to_time = int(end_date.timestamp())
            
            # Get data from TradingView
            data = self.tv.get_hist(
                symbol=f"PSX:{symbol}",
                exchange="PSX",
                interval=self.interval,
                from_time=from_time,
                to_time=to_time,
                n_bars=5000  # Maximum number of bars
            )
            
            if data is None or len(data) == 0:
                raise ValueError(f"No data returned for symbol {symbol}")
                
            # Ensure the index is datetime
            if not isinstance(data.index, pd.DatetimeIndex):
                data.index = pd.to_datetime(data.index)
                
            return data
            
        except Exception as e:
            raise ValueError(f"Failed to fetch historical data: {str(e)}") 