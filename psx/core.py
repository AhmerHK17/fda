from datetime import datetime, timedelta
from typing import Optional, Union, List, Dict, Any
import pandas as pd

from .exceptions import PSXRequestError
from .psx_reader import PSXDataReader, psx_reader

__all__ = ['PSXTicker', 'PSXDataReader']

class PSXTicker:
    def __init__(self, symbol: str):
        """
        Initialize a PSX ticker instance
        
        Args:
            symbol: Stock symbol (e.g. 'HBL')
        """
        self.symbol = symbol.upper()
        
    def get_intraday_data(self) -> pd.DataFrame:
        """
        Get current intraday data
        
        Returns:
            DataFrame containing timestamp-indexed price and volume data
        """
        try:
            return psx_reader.get_intraday_data(self.symbol)
        except Exception as e:
            raise PSXRequestError(f"Failed to fetch intraday data: {str(e)}")
        
    def get_historical_data(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = "1mo"
    ) -> pd.DataFrame:
        """
        Get historical daily data
        
        Args:
            start_date: Start date for data (default: period ago)
            end_date: End date for data (default: today)
            period: Time period (e.g. '1mo', '3mo', '6mo', '1y')
            
        Returns:
            DataFrame with historical OHLCV data
        """
        if end_date is None:
            end_date = datetime.now()
            
        if start_date is None:
            # Parse period string
            value = int(period[:-2])
            unit = period[-2:]
            
            if unit == 'mo':
                start_date = end_date - timedelta(days=value * 30)
            elif unit == 'y':
                start_date = end_date - timedelta(days=value * 365)
            else:
                raise ValueError("Invalid period format. Use 'Xmo' or 'Xy' (e.g. '1mo', '1y')")
        
        try:
            # Convert datetime to date objects
            start_date_date = start_date.date()
            end_date_date = end_date.date()
            
            return psx_reader.get_historical_data(
                self.symbol, 
                start_date=start_date_date, 
                end_date=end_date_date
            )
        except Exception as e:
            raise PSXRequestError(f"Failed to fetch historical data: {str(e)}") 