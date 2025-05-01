from psx import PSXTicker

def test_basic():
    try:
        # Create a PSXTicker instance
        pso = PSXTicker("PSO")
        print("Successfully created PSXTicker instance")
        
        # Try to fetch data
        data = pso.get_intraday_data()
        print("\nSuccessfully fetched data:")
        print(data.head())
        
        # Try to get latest price
        price = pso.latest_price
        print(f"\nLatest price: {price}")
        
        return True
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    test_basic() 