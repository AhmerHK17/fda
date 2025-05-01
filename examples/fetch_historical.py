from datetime import datetime, timedelta
from psx import PSXTicker

def main():
    # Create a PSXTicker instance for PSO (Pakistan State Oil)
    pso = PSXTicker("PSO")
    
    # Get historical data for the last month
    print("Fetching historical data for PSO...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    historical_data = pso.get_historical_data(start_date=start_date, end_date=end_date)
    print("\nHistorical data (last 5 entries):")
    print(historical_data.tail())
    
    # Get OHLC data for different periods
    print("\nOHLC data for different periods:")
    periods = ["1d", "5d", "1mo", "3mo"]
    for period in periods:
        print(f"\n{period} OHLC data:")
        ohlc_data = pso.get_ohlc(period=period)
        print(ohlc_data.tail(1))

if __name__ == "__main__":
    main() 