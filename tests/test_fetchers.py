#!/usr/bin/env python
"""
Test script for PSX fetchers functionality.
Tests both intraday and historical data fetching.
"""
import sys
from datetime import datetime, timedelta
from psx.fetchers import fetch_intraday_data, fetch_historical_data, parse_intraday_data
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

# Test URLs
COMPANY_URL = "https://dps.psx.com.pk/company/HBL"
HISTORICAL_URL = "https://dps.psx.com.pk/historical"

# Headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

def test_intraday_fetching():
    """Test fetching intraday data."""
    print("\n=== Testing Intraday Data Fetching ===")
    
    # Test with a known symbol
    symbol = "PSO"
    print(f"Fetching intraday data for {symbol}...")
    
    try:
        # Fetch the data
        data = fetch_intraday_data(symbol)
        
        # Parse the data into a DataFrame
        df = parse_intraday_data(data)
        
        # Print the results
        print(f"Successfully fetched intraday data for {symbol}")
        print(f"Data shape: {df.shape}")
        print("\nFirst 5 rows:")
        print(df.head())
        
        return True
    except Exception as e:
        print(f"Error fetching intraday data: {str(e)}")
        return False

def test_historical_fetching():
    """Test fetching historical data."""
    print("\n=== Testing Historical Data Fetching ===")
    
    # Test with a known symbol
    symbol = "PSO"
    
    # Get data for the last month
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    print(f"Fetching historical data for {symbol} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    
    try:
        # Fetch the data
        data, available_dates = fetch_historical_data(symbol, start_date, end_date)
        
        # Print the results
        print(f"Successfully fetched historical data for {symbol}")
        print(f"Number of available dates: {len(available_dates)}")
        if available_dates:
            print(f"Date range: {available_dates[0]} to {available_dates[-1]}")
        
        return True
    except Exception as e:
        print(f"Error fetching historical data: {str(e)}")
        return False

def test_company_page():
    """Test fetching and parsing the company page"""
    print("Testing company page...")
    response = requests.get(COMPANY_URL, headers=HEADERS)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for the quote section
        quote_section = soup.find('div', {'id': 'quote'})
        if quote_section:
            print("Found quote section")
            print(quote_section.prettify()[:500])  # Print first 500 chars
        else:
            print("Quote section not found")
            # Try to find any relevant sections
            for div in soup.find_all('div', class_=True):
                print(f"Found div with class: {div.get('class')}")
        
        # Save the HTML for inspection
        with open("company_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved HTML to company_page.html")
    else:
        print(f"Failed to fetch company page: {response.status_code}")

def test_historical_page():
    """Test fetching and parsing the historical data page"""
    print("\nTesting historical page...")
    
    # Format dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    # Construct URL with parameters
    url = f"{HISTORICAL_URL}?symbol=HBL&from={start_str}&to={end_str}"
    print(f"URL: {url}")
    
    response = requests.get(url, headers=HEADERS)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for i, table in enumerate(tables):
            print(f"\nTable {i+1}:")
            print(f"Classes: {table.get('class')}")
            print(f"ID: {table.get('id')}")
            print(table.prettify()[:500])  # Print first 500 chars
        
        # Save the HTML for inspection
        with open("historical_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved HTML to historical_page.html")
    else:
        print(f"Failed to fetch historical page: {response.status_code}")

def main():
    """Run all tests."""
    print("=== PSX Fetchers Test ===")
    print(f"Python version: {sys.version}")
    
    # Test intraday fetching
    intraday_success = test_intraday_fetching()
    
    # Test historical fetching
    historical_success = test_historical_fetching()
    
    # Test company page
    company_page_success = test_company_page()
    
    # Test historical page
    historical_page_success = test_historical_page()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Intraday fetching test: {'✓ PASSED' if intraday_success else '✗ FAILED'}")
    print(f"Historical fetching test: {'✓ PASSED' if historical_success else '✗ FAILED'}")
    print(f"Company page test: {'✓ PASSED' if company_page_success else '✗ FAILED'}")
    print(f"Historical page test: {'✓ PASSED' if historical_page_success else '✗ FAILED'}")
    
    if intraday_success and historical_success and company_page_success and historical_page_success:
        print("\nAll tests passed! The PSX fetchers are working correctly.")
    else:
        print("\nSome tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 