from datetime import datetime
from psx import PSXTicker

def main():
    # Create a PSXTicker instance for PSO (Pakistan State Oil)
    pso = PSXTicker("PSO")
    
    try:
        # First, get the available data range
        earliest_date, latest_date = pso.get_data_range()
        print(f"Available data range: {earliest_date.strftime('%Y-%m-%d')} to {latest_date.strftime('%Y-%m-%d')}")
        
        # Define date range (use available range if possible)
        start_date = max(datetime(2023, 4, 1), earliest_date)
        end_date = min(datetime(2025, 4, 30), latest_date)
        
        print(f"\nFetching PSO historical data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
        
        # Fetch historical data
        historical_data = pso.get_historical_data(start_date=start_date, end_date=end_date)
        
        # Display summary
        print(f"\nTotal days of data: {len(historical_data)}")
        
        # Display first 5 entries
        print("\nFirst 5 entries:")
        print(historical_data.head())
        
        # Display last 5 entries
        print("\nLast 5 entries:")
        print(historical_data.tail())
        
        # Calculate some statistics
        print("\nPrice Statistics:")
        print(f"Average price: {historical_data['close'].mean():.2f}")
        print(f"Highest price: {historical_data['high'].max():.2f}")
        print(f"Lowest price: {historical_data['low'].min():.2f}")
        print(f"Total volume: {historical_data['volume'].sum():,.0f}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 