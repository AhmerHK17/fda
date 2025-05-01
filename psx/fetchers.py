import requests
import datetime
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime, timedelta
import pandas as pd
import re
import json
from bs4 import BeautifulSoup
from .exceptions import PSXConnectionError, PSXDataError, PSXRequestError
from .utils import parse_timeseries_data
from .auth import TVSession
from .psx_reader import psx_reader

# Constants
BASE_URL = "https://dps.psx.com.pk"
COMPANY_URL = f"{BASE_URL}/company"
HISTORICAL_URL = f"{BASE_URL}/historical"
API_URL = f"{BASE_URL}/api"

# Custom exception for PSX API requests
class PSXRequestError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(self.message)

# Default headers to mimic a browser
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': BASE_URL,
    'Referer': f'{BASE_URL}/',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}

def format_date(date: datetime) -> str:
    """Format date for PSX API requests"""
    return date.strftime("%Y-%m-%d")

def parse_float(value: str) -> float:
    """Parse string to float, handling commas and dashes"""
    try:
        return float(value.replace(',', '').replace('-', '0'))
    except (ValueError, AttributeError):
        return 0.0

def fetch_intraday_data(symbol: str) -> Dict[str, Any]:
    """
    Fetch intraday data for a given symbol from PSX timeseries API
    
    Args:
        symbol: Stock symbol (e.g. 'PSO')
        
    Returns:
        Dictionary containing intraday data with latest price, change and volume
    
    Raises:
        PSXRequestError: If request fails or data not found
    """
    url = f"{BASE_URL}/timeseries/int/{symbol}"
    
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS)
        response.raise_for_status()
        
        if response.status_code == 404:
            raise PSXRequestError(f"Symbol {symbol} not found")
            
        data = response.json()
        
        if not data or 'data' not in data or not data['data']:
            raise PSXRequestError(f"No intraday data available for {symbol}")
            
        # Data is in format: [timestamp, price, volume]
        timeseries_data = data['data']
        
        if not timeseries_data:
            return {
                'symbol': symbol,
                'price': 0.0,
                'change': 0.0,
                'change_percent': 0.0,
                'volume': 0
            }
            
        # Sort by timestamp to get latest first
        timeseries_data.sort(key=lambda x: x[0], reverse=True)
        
        # Get latest price
        latest_price = float(timeseries_data[0][1])
        
        # Calculate total volume for today
        total_volume = sum(float(entry[2]) for entry in timeseries_data)
        
        # Get opening price (last entry is earliest)
        opening_price = float(timeseries_data[-1][1])
        
        # Calculate change
        price_change = latest_price - opening_price
        price_change_percent = (price_change / opening_price) * 100 if opening_price > 0 else 0.0
        
        return {
            'symbol': symbol,
            'price': latest_price,
            'change': round(price_change, 2),
            'change_percent': round(price_change_percent, 2),
            'volume': int(total_volume)
        }
        
    except requests.exceptions.RequestException as e:
        raise PSXRequestError(f"Failed to fetch data for {symbol}: {str(e)}")
    except (ValueError, KeyError, IndexError) as e:
        raise PSXDataError(f"Error parsing data for {symbol}: {str(e)}")

def fetch_historical_data(symbol: str, from_date: datetime, to_date: datetime) -> pd.DataFrame:
    """
    Fetch historical data for a given symbol between two dates.
    
    Args:
        symbol: Stock symbol
        from_date: Start date
        to_date: End date
        
    Returns:
        DataFrame with historical data
    """
    try:
        # Format dates for API request
        from_str = from_date.strftime('%Y-%m-%d')
        to_str = to_date.strftime('%Y-%m-%d')
        
        # First try the new API endpoint
        url = f"{API_URL}/historical/equities"
        params = {
            'symbol': symbol,
            'from': from_str,
            'to': to_str
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 404:
            # Try fallback to old endpoint
            url = f"{API_URL}/historical"
            response = requests.get(url, params=params)
            
        if response.status_code == 401:
            raise PSXRequestError("Unauthorized access to PSX API")
            
        if response.status_code != 200:
            raise PSXRequestError(f"Failed to fetch historical data: HTTP {response.status_code}")
            
        try:
            data = response.json()
        except ValueError:
            raise PSXRequestError("Invalid JSON response from PSX API")
            
        # Handle both new and old API response formats
        if 'data' in data:
            # New API format
            records = data['data']
            if not records:
                return pd.DataFrame()
                
            df = pd.DataFrame(records)
            
        else:
            # Old API format - parse HTML table
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'historical-data'})
            
            if not table:
                raise PSXRequestError("Could not find historical data table")
                
            headers = []
            for th in table.find_all('th'):
                headers.append(th.text.strip())
                
            rows = []
            for tr in table.find_all('tr')[1:]:  # Skip header row
                row = []
                for td in tr.find_all('td'):
                    row.append(td.text.strip())
                if row:
                    rows.append(row)
                    
            df = pd.DataFrame(rows, columns=headers)
            
        # Standardize column names
        column_map = {
            'Date': 'date',
            'Open': 'open', 
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'Change': 'change'
        }
        df = df.rename(columns=column_map)
        
        # Convert types
        df['date'] = pd.to_datetime(df['date'])
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')
                
        # Sort by date
        df = df.sort_values('date')
        
        return df
        
    except requests.exceptions.RequestException as e:
        raise PSXRequestError(f"Request failed: {str(e)}")
    except Exception as e:
        raise PSXRequestError(f"Error fetching historical data: {str(e)}")

def scrape_historical_data(symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Scrape historical data from PSX website using PSXDataReader
    
    Args:
        symbol: Stock symbol
        start_date: Start date
        end_date: End date
        
    Returns:
        DataFrame with historical data
    """
    try:
        # Convert datetime to date objects
        start = start_date.date()
        end = end_date.date()
        
        # Use the PSXDataReader to fetch data
        df = psx_reader.get_historical_data(symbol, start, end)
        
        # Filter by date range
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        
        return df
        
    except Exception as e:
        raise PSXRequestError(f"Failed to scrape historical data: {str(e)}")

def format_date_for_api(date: Union[datetime, str]) -> str:
    """
    Format a date object or string for the PSX API.
    
    Args:
        date (Union[datetime, str]): Date to format
        
    Returns:
        str: Formatted date string
    """
    if isinstance(date, str):
        try:
            date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date string must be in YYYY-MM-DD format")
    
    return date.strftime('%Y-%m-%d')

def parse_intraday_data(json_data: Dict) -> pd.DataFrame:
    """
    Parse intraday data from JSON response into a pandas DataFrame.
    
    Args:
        json_data (Dict): JSON response from the intraday API
        
    Returns:
        pd.DataFrame: Parsed intraday data
    """
    if not json_data or 'data' not in json_data:
        return pd.DataFrame()
    
    # Extract data from the response
    data = json_data['data']
    
    # Create a list to store the parsed data
    parsed_data = []
    
    for entry in data:
        if isinstance(entry, list) and len(entry) >= 3:
            timestamp, price, volume = entry
            # Convert timestamp to datetime
            dt = datetime.fromtimestamp(timestamp)
            parsed_data.append({
                'timestamp': dt,
                'price': price,
                'volume': volume
            })
    
    # Create DataFrame
    df = pd.DataFrame(parsed_data)
    
    # Set timestamp as index
    if not df.empty:
        df.set_index('timestamp', inplace=True)
    
    return df

def _fetch_historical_data_scrape(
    symbol: Union[str, List[str]], 
    start_date: datetime, 
    end_date: datetime
) -> Optional[Dict[str, Any]]:
    """
    Fetch historical data using direct scraping approach (psx-data-reader method).
    
    Args:
        symbol: Stock symbol or list of symbols
        start_date: Start date for historical data
        end_date: End date for historical data
        
    Returns:
        Dictionary containing historical data or None if scraping fails
    """
    try:
        # Convert single symbol to list for consistent handling
        symbols = [symbol] if isinstance(symbol, str) else symbol
        
        # Prepare data for scraping
        data_entries = []
        available_dates = []
        
        for sym in symbols:
            # Format dates for the request
            start_str = format_date(start_date)
            end_str = format_date(end_date)
            
            # Use PSXDataReader to fetch data
            df = psx_reader.get_historical_data(sym, start_date.date(), end_date.date())
            
            if not df.empty:
                # Convert DataFrame to PSX API format
                for date, row in df.iterrows():
                    entry = [
                        date.strftime("%Y-%m-%d"),
                        float(row['Open']),
                        float(row['High']),
                        float(row['Low']),
                        float(row['Close']),
                        float(row['Volume'])
                    ]
                    data_entries.append(entry)
                    available_dates.append(date)
        
        # Sort dates chronologically
        available_dates.sort()
        
        if not data_entries:
            return None
            
        return {
            "data": data_entries,
            "symbol": symbols[0] if len(symbols) == 1 else symbols,
            "exchange": "PSX",
            "interval": "1d"
        }
        
    except Exception as e:
        # Log error but don't raise - we'll try other methods
        print(f"Scraping error: {str(e)}")
        return None

def _extract_available_dates(data: Dict[str, Any]) -> List[datetime]:
    """Extract and sort available dates from response data."""
    available_dates = []
    if "data" in data and isinstance(data["data"], list):
        for entry in data["data"]:
            if isinstance(entry, list) and len(entry) > 0:
                try:
                    date_str = entry[0]
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    available_dates.append(date)
                except (ValueError, TypeError):
                    continue
    
    # Sort dates chronologically
    available_dates.sort()
    return available_dates

def _convert_tv_data_to_psx_format(analysis: Any, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """
    Convert TradingView analysis data to PSX API format.
    
    Args:
        analysis: TradingView analysis object
        start_date: Start date for filtering
        end_date: End date for filtering
        
    Returns:
        Dictionary in PSX API format
    """
    indicators = analysis.indicators
    
    # Create data entries in PSX format: [date, open, high, low, close, volume]
    data_entries = []
    
    # Get the date from analysis (usually current date)
    current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Add entry if within date range
    if start_date <= current_date <= end_date:
        entry = [
            current_date.strftime("%Y-%m-%d"),
            indicators.get("open", 0),
            indicators.get("high", 0),
            indicators.get("low", 0),
            indicators.get("close", 0),
            indicators.get("volume", 0)
        ]
        data_entries.append(entry)
    
    return {
        "data": data_entries,
        "symbol": analysis.symbol,
        "exchange": "PSX",
        "interval": "1d"
    } 