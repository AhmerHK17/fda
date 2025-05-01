import sys
print("Python path:", sys.path)

try:
    from psx import PSXTicker
    print("Successfully imported PSXTicker")
    
    # Try to create an instance
    ticker = PSXTicker("PSO")
    print("Successfully created PSXTicker instance")
    
except ImportError as e:
    print("Import error:", str(e))
except Exception as e:
    print("Other error:", str(e)) 