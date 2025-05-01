import requests
from datetime import datetime, timedelta

# Browser-like headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://www.psx.com.pk',
    'Referer': 'https://www.psx.com.pk/',
}

def test_endpoints():
    """Test different PSX API endpoints."""
    symbol = "PSO"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Test endpoints
    endpoints = [
        f"https://dps.psx.com.pk/api/timeseries/int/{symbol}",
        f"https://dps.psx.com.pk/api/market/historical/{symbol}",
        f"https://www.psx.com.pk/psx/api/psx/market/stock/{symbol}",
        f"https://www.psx.com.pk/market/EQTY/stocks/{symbol}/historical",
        f"https://www.psx.com.pk/market/EQTY/stocks/{symbol}/intraday"
    ]
    
    for url in endpoints:
        print(f"\nTesting endpoint: {url}")
        try:
            params = {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            }
            
            response = requests.get(url, headers=headers, params=params)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("Response data:")
                print(data)
            else:
                print(f"Error response: {response.text}")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_endpoints() 