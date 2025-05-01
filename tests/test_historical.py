import sys
import os
import json
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from psx.fetchers import fetch_historical_data, PSXRequestError

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from psx.fetchers import scrape_historical_data

def debug_api_response():
    """Debug the API response for historical data"""
    symbol = "HBL"
    from_date = datetime(2022, 10, 1)
    to_date = datetime(2025, 3, 31)
    
    # Format dates
    from_str = from_date.strftime('%Y-%m-%d')
    to_str = to_date.strftime('%Y-%m-%d')
    
    # Try both endpoints
    endpoints = [
        "https://dps.psx.com.pk/api/historical/equities",
        "https://dps.psx.com.pk/api/historical"
    ]
    
    for endpoint in endpoints:
        print(f"\nTrying endpoint: {endpoint}")
        params = {
            'symbol': symbol,
            'from': from_str,
            'to': to_str
        }
        
        try:
            response = requests.get(endpoint, params=params)
            print(f"Status code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            content = response.text
            print(f"\nResponse content length: {len(content)}")
            print("First 500 characters of response:")
            print(content[:500])
            
            try:
                data = response.json()
                print("\nJSON data structure:")
                if isinstance(data, dict):
                    print(f"Dictionary with keys: {list(data.keys())}")
                    if 'data' in data:
                        print(f"Length of data list: {len(data['data'])}")
                elif isinstance(data, list):
                    print(f"List with {len(data)} items")
                else:
                    print(f"Unexpected type: {type(data)}")
            except json.JSONDecodeError:
                print("\nResponse is not JSON. Checking for HTML table...")
                if '<table' in content:
                    print("Found HTML table in response")
                else:
                    print("No HTML table found in response")
                    
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")

def main():
    print("Starting historical data debug test...")
    debug_api_response()
    
    print("\nTesting fetch_historical_data function...")
    try:
        df = fetch_historical_data(
            symbol="HBL",
            from_date=datetime(2022, 10, 1),
            to_date=datetime(2025, 3, 31)
        )
        print(f"\nDataFrame shape: {df.shape}")
        if not df.empty:
            print("\nFirst few rows:")
            print(df.head())
            print("\nLast few rows:")
            print(df.tail())
        else:
            print("No data returned")
    except PSXRequestError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main() 