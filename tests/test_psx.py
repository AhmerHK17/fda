#!/usr/bin/env python
"""
Test script for PSX library functionality.
Tests both historical and intraday data fetching.
"""
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from psx import PSXTicker

def test_single_symbol():
    """Test fetching data for a single symbol."""
    print("\n=== Testing Single Symbol (PSO) ===")
    
    # Create a ticker for Pakistan State Oil
    pso = PSXTicker("PSO")
    
    # Get historical data for the last month
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    print(f"Fetching historical data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    
    try:
        hist_data = pso.get_historical_data(start_date=start_date, end_date=end_date)
        print(f"Historical data shape: {hist_data.shape}")
        print("\nFirst 5 rows of historical data:")
        print(hist_data.head())
        
        # Get today's data
        print("\nFetching intraday data...")
        today_data = pso.get_intraday_data()
        print(f"Intraday data shape: {today_data.shape}")
        print("\nFirst 5 rows of intraday data:")
        print(today_data.head())
        
        # Get latest price
        print(f"\nLatest price: {pso.latest_price}")
        
        # Get data range
        earliest, latest = pso.get_data_range()
        print(f"\nAvailable data range: {earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}")
        
        return True
    except Exception as e:
        print(f"Error testing single symbol: {str(e)}")
        return False

def test_multiple_symbols():
    """Test fetching data for multiple symbols."""
    print("\n=== Testing Multiple Symbols (PSO, OGDC, HBL) ===")
    
    # Create tickers for multiple symbols
    stocks = PSXTicker(["PSO", "OGDC", "HBL"])
    
    # Get historical data for the last week
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    print(f"Fetching historical data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    
    try:
        hist_data = stocks.get_historical_data(start_date=start_date, end_date=end_date)
        print(f"Historical data shape: {hist_data.shape}")
        print("\nFirst 5 rows of historical data:")
        print(hist_data.head())
        
        # Get today's data
        print("\nFetching intraday data...")
        today_data = stocks.get_intraday_data()
        print(f"Intraday data shape: {today_data.shape}")
        print("\nFirst 5 rows of intraday data:")
        print(today_data.head())
        
        # Get latest prices
        print("\nLatest prices:")
        for symbol, price in stocks.latest_price.items():
            print(f"{symbol}: {price}")
        
        return True
    except Exception as e:
        print(f"Error testing multiple symbols: {str(e)}")
        return False

def test_period_fetching():
    """Test fetching data using period parameters."""
    print("\n=== Testing Period Fetching ===")
    
    # Create a ticker
    pso = PSXTicker("PSO")
    
    # Test different periods
    periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y"]
    
    for period in periods:
        print(f"\nFetching {period} data...")
        try:
            data = pso.get_ohlc(period=period)
            print(f"Data shape: {data.shape}")
            print(f"Date range: {data.index.min()} to {data.index.max()}")
        except Exception as e:
            print(f"Error fetching {period} data: {str(e)}")

def main():
    """Run all tests."""
    print("=== PSX Library Test ===")
    print(f"Python version: {sys.version}")
    print(f"Pandas version: {pd.__version__}")
    
    # Test single symbol
    single_symbol_success = test_single_symbol()
    
    # Test multiple symbols
    multiple_symbols_success = test_multiple_symbols()
    
    # Test period fetching
    test_period_fetching()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Single symbol test: {'✓ PASSED' if single_symbol_success else '✗ FAILED'}")
    print(f"Multiple symbols test: {'✓ PASSED' if multiple_symbols_success else '✗ FAILED'}")
    
    if single_symbol_success and multiple_symbols_success:
        print("\nAll tests passed! The PSX library is working correctly.")
    else:
        print("\nSome tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 