from psx import PSXTicker

def main():
    # Create a PSXTicker instance for PSO (Pakistan State Oil)
    pso = PSXTicker("PSO")
    
    # Fetch intraday data
    print("Fetching intraday data for PSO...")
    data = pso.get_intraday_data()
    print("\nLatest 5 entries:")
    print(data.tail())
    
    # Get latest price
    print(f"\nLatest price: {pso.latest_price}")

if __name__ == "__main__":
    main() 