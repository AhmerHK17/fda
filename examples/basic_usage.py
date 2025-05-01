from datetime import datetime
from psx.core import PSXTicker

def main():
    # Create a ticker instance
    ticker = PSXTicker('HBL')
    
    # Get intraday data
    print("\nFetching intraday data for HBL:")
    intraday_data = ticker.get_intraday_data()
    print(intraday_data.head())
    
    # Get historical data
    print("\nFetching historical data for HBL (last 3 months):")
    end_date = datetime.now()
    start_date = end_date.replace(month=end_date.month-3)
    historical_data = ticker.get_historical_data(start_date=start_date, end_date=end_date)
    print(historical_data.head())
    
    # Print some statistics
    print("\nHistorical Data Statistics:")
    print(f"Date Range: {historical_data.index.min()} to {historical_data.index.max()}")
    print(f"Total Trading Days: {len(historical_data)}")
    print(f"Average Close Price: {historical_data['close'].mean():.2f}")
    print(f"Highest Price: {historical_data['high'].max():.2f}")
    print(f"Lowest Price: {historical_data['low'].min():.2f}")
    print(f"Total Volume: {historical_data['volume'].sum():,.0f}")

if __name__ == "__main__":
    main() 