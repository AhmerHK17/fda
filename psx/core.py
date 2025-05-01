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
        
        def get_dividend_announcements(self, max_results: int = 20) -> pd.DataFrame:
        """
        Scrape dividend announcements from PSX financial announcements page.
        
        Args:
            max_results: Max number of dividend records to return

        Returns:
            DataFrame with dividend announcements for the company
        """
        url = 'https://www.psx.com.pk/psx/announcement/financial-announcements'
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            raise PSXRequestError(f"Failed to fetch dividend announcements: {str(e)}")

        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find('table')

        if not table:
            raise ValueError("No table found on the PSX announcements page.")

        rows = table.find_all('tr')
        data = []
        for row in rows[1:]:  # Skip header
            cols = row.find_all('td')
            if len(cols) < 5:
                continue

            symbol = cols[0].text.strip()
            announcement_type = cols[2].text.strip()
            announcement_detail = cols[3].text.strip()
            date = cols[4].text.strip()

            if self.symbol in symbol and 'Dividend' in announcement_type:
                data.append({
                    'Symbol': symbol,
                    'Type': announcement_type,
                    'Detail': announcement_detail,
                    'Date': date
                })

            if len(data) >= max_results:
                break

        return pd.DataFrame(data)
