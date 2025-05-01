from datetime import datetime, timedelta
import pandas as pd
from psx.core import PSXTicker
import traceback

def test_hbl_data():
    # Create HBL ticker instance
    ticker = PSXTicker('HBL')
    
    print("\n=== Testing HBL Intraday Data ===")
    try:
        # Get intraday data
        intraday_data = ticker.get_intraday_data()
        print("\nIntraday Data Sample:")
        print(intraday_data.head())
        
        # Basic validation
        assert isinstance(intraday_data, pd.DataFrame)
        assert not intraday_data.empty
        assert 'price' in intraday_data.columns
        assert 'volume' in intraday_data.columns
        assert isinstance(intraday_data.index, pd.DatetimeIndex)
        
        print("\nIntraday Data Validation:")
        print(f"Number of records: {len(intraday_data)}")
        print(f"Latest timestamp: {intraday_data.index.max()}")
        print(f"Latest price: {intraday_data['price'].iloc[-1]}")
        print(f"Latest volume: {intraday_data['volume'].iloc[-1]}")
        print("\n✅ Intraday data test passed!")
    except Exception as e:
        print(f"\n❌ Error fetching intraday data:")
        print(traceback.format_exc())
    
    print("\n=== Testing HBL Historical Data ===")
    try:
        # Get historical data for last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        print(f"\nFetching data from {start_date.date()} to {end_date.date()}")
        historical_data = ticker.get_historical_data(
            start_date=start_date,
            end_date=end_date
        )
        
        print("\nHistorical Data Sample:")
        print(historical_data.head())
        
        # Basic validation
        assert isinstance(historical_data, pd.DataFrame)
        assert not historical_data.empty
        assert all(col in historical_data.columns for col in ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME'])
        assert isinstance(historical_data.index, pd.DatetimeIndex)
        
        print("\nHistorical Data Statistics:")
        print(f"Date Range: {historical_data.index.min()} to {historical_data.index.max()}")
        print(f"Total Trading Days: {len(historical_data)}")
        print(f"Average Close Price: {historical_data['CLOSE'].mean():.2f}")
        print(f"Highest Price: {historical_data['HIGH'].max():.2f}")
        print(f"Lowest Price: {historical_data['LOW'].min():.2f}")
        print(f"Total Volume: {historical_data['VOLUME'].sum():,.0f}")
        print("\n✅ Historical data test passed!")
    except Exception as e:
        print(f"\n❌ Error fetching historical data:")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_hbl_data() 