from concurrent.futures import ThreadPoolExecutor, as_completed
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime, date
from typing import Union, List, Optional
import threading
import pandas as pd
import numpy as np
import requests
from tqdm import tqdm

from .exceptions import PSXRequestError, PSXConnectionError, PSXDataError

class PSXDataReader:
    """
    A class for fetching historical data directly from the PSX website.
    This implementation is based on the psx-data-reader project.
    """
    
    # Constants
    BASE_URL = "https://dps.psx.com.pk"
    HISTORY_URL = f"{BASE_URL}/historical"
    SYMBOLS_URL = f"{BASE_URL}/symbols"
    TIMESERIES_URL = f"{BASE_URL}/timeseries/int"
    HEADERS = ['TIME', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']
    
    def __init__(self):
        """Initialize the PSX data reader with a session for making requests."""
        self.__local = threading.local()
        
    @property
    def session(self):
        """Get or create a session for making requests."""
        if not hasattr(self.__local, "session"):
            self.__local.session = requests.Session()
            # Set default headers to mimic a browser
            self.__local.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Origin': self.BASE_URL,
                'Referer': f'{self.BASE_URL}/',
            })
        return self.__local.session
    
    def get_tickers(self) -> pd.DataFrame:
        """
        Get a list of all available tickers from PSX.
        
        Returns:
            DataFrame containing ticker information
        """
        try:
            response = self.session.get(self.SYMBOLS_URL)
            response.raise_for_status()
            return pd.read_json(self.SYMBOLS_URL)
        except Exception as e:
            raise PSXConnectionError(f"Failed to fetch tickers: {str(e)}")
    
    def get_historical_data(
        self, 
        symbol: str, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Fetch historical data for a single symbol between start_date and end_date.
        
        Args:
            symbol: Stock symbol (e.g., 'HBL')
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            DataFrame with historical OHLCV data
        """
        # Set default dates if not provided
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - relativedelta(months=1)
            
        # Generate list of dates to fetch (one per month)
        dates = self._generate_date_range(start_date, end_date)
        
        # Fetch data for each date in parallel
        data = []
        futures = []
        
        with tqdm(total=len(dates), desc=f"Downloading {symbol}'s Data") as progressbar:
            with ThreadPoolExecutor(max_workers=6) as executor:
                for date_obj in dates:
                    futures.append(
                        executor.submit(self._download_data, symbol=symbol, date=date_obj)
                    )
                
                for future in as_completed(futures):
                    result = future.result()
                    if isinstance(result, pd.DataFrame):
                        data.append(result)
                    progressbar.update(1)
        
        # Combine and preprocess the data
        if not data:
            return pd.DataFrame()
            
        return self._preprocess_data(data)
    
    def get_multiple_symbols(
        self, 
        symbols: Union[str, List[str]], 
        start_date: date, 
        end_date: date
    ) -> pd.DataFrame:
        """
        Fetch historical data for multiple symbols between start_date and end_date.
        
        Args:
            symbols: Stock symbol or list of symbols
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            DataFrame with historical OHLCV data for all symbols
        """
        # Convert single symbol to list for consistent handling
        symbols_list = [symbols] if isinstance(symbols, str) else symbols
        
        # Fetch data for each symbol
        data = [
            self.get_historical_data(symbol, start_date, end_date) 
            for symbol in symbols_list
        ]
        
        # Filter out empty DataFrames
        data = [df for df in data if not df.empty]
        
        if not data:
            return pd.DataFrame()
            
        # If only one symbol, return its DataFrame
        if len(data) == 1:
            return data[0]
            
        # Combine DataFrames with multi-index
        return pd.concat(data, keys=symbols_list, names=["Symbol", "Date"])
    
    def _download_data(self, symbol: str, date: date) -> pd.DataFrame:
        """
        Download historical data for a symbol on a specific date.
        
        Args:
            symbol: Stock symbol
            date: Date to fetch data for
            
        Returns:
            DataFrame with historical data for the specified date
        """
        try:
            # Prepare POST data
            post_data = {
                "month": date.month, 
                "year": date.year, 
                "symbol": symbol
            }
            
            # Make request
            response = self.session.post(self.HISTORY_URL, data=post_data)
            response.raise_for_status()
            
            # Parse HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract data from HTML table
            return self._parse_html_table(soup)
            
        except Exception as e:
            raise PSXRequestError(f"Failed to download data for {symbol} on {date}: {str(e)}")
    
    def _parse_html_table(self, soup: BeautifulSoup) -> pd.DataFrame:
        """
        Parse HTML table from PSX website into a DataFrame.
        
        Args:
            soup: BeautifulSoup object with parsed HTML
            
        Returns:
            DataFrame with historical data
        """
        stocks = defaultdict(list)
        rows = soup.select("tr")
        
        for row in rows:
            cols = [col.getText().strip() for col in row.select("td")]
            
            # Skip rows without enough columns
            if len(cols) < len(self.HEADERS):
                continue
                
            # Map columns to headers
            for key, value in zip(self.HEADERS, cols):
                if key == "TIME":
                    try:
                        value = datetime.strptime(value, "%b %d, %Y")
                    except ValueError:
                        # Skip rows with invalid dates
                        continue
                stocks[key].append(value)
        
        # Create DataFrame
        if not stocks["TIME"]:
            return pd.DataFrame()
            
        df = pd.DataFrame(stocks, columns=self.HEADERS)
        df = df.set_index("TIME")
        
        return df
    
    def _generate_date_range(self, start: date, end: date) -> List[date]:
        """
        Generate a list of dates (one per month) between start and end.
        
        Args:
            start: Start date
            end: End date
            
        Returns:
            List of dates (one per month)
        """
        period = end - start
        number_of_months = period.days // 30
        current_date = datetime(start.year, start.month, 1).date()
        dates = [current_date]
        
        for _ in range(number_of_months):
            prev_date = dates[-1]
            next_date = prev_date + relativedelta(months=1)
            dates.append(next_date)
        
        # Ensure we have at least one date
        if not dates:
            dates = [start]
            
        return dates
    
    def _preprocess_data(self, data: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Preprocess a list of DataFrames into a single DataFrame.
        
        Args:
            data: List of DataFrames to combine and process
            
        Returns:
            Processed DataFrame with numeric columns
        """
        if not data:
            return pd.DataFrame()
            
        # Combine all DataFrames
        df = pd.concat(data)
        
        # Remove duplicates and sort by date
        df = df.loc[~df.index.duplicated(keep='last')]
        df = df.sort_index()
        
        # Convert numeric columns
        numeric_cols = ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']
        for col in numeric_cols:
            if col in df.columns:
                # Remove commas and convert to numeric
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(',', ''), 
                    errors='coerce'
                )
        
        return df

    def get_intraday_data(self, symbol: str) -> pd.DataFrame:
        """
        Fetch real-time intraday data for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'PSO')
            
        Returns:
            DataFrame with columns: timestamp, price, volume
        """
        try:
            url = f"{self.TIMESERIES_URL}/{symbol}"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] != 1 or not data.get("data"):
                raise PSXDataError(f"No intraday data available for {symbol}")
                
            # Convert data to DataFrame
            df = pd.DataFrame(data["data"], columns=["timestamp", "price", "volume"])
            
            # Convert timestamp to datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
            
            # Set timestamp as index
            df.set_index("timestamp", inplace=True)
            
            # Sort by timestamp
            df.sort_index(inplace=True)
            
            return df
            
        except Exception as e:
            raise PSXConnectionError(f"Failed to fetch intraday data for {symbol}: {str(e)}")


# Create a singleton instance
psx_reader = PSXDataReader() 