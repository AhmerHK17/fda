# PyPSX

A Python library for fetching Pakistan Stock Exchange (PSX) data, similar to yfinance but specifically for Pakistani stocks.

## Features

- Fetch real-time intraday data from PSX API
- Get historical OHLCV data from PSX API
- Support for multiple symbols
- Clean pandas DataFrame output
- Error handling and retries

## Installation

```bash
# Install from PyPI (when published)
pip install pypsx

# Install from source
git clone https://github.com/amaanjbutt/pyPSX.git
cd pyPSX
pip install -e .
```

## Quick Start

```python
from datetime import datetime
from psx.core import PSXTicker

# Create a ticker instance
ticker = PSXTicker('HBL')

# Get intraday data
intraday_data = ticker.get_intraday_data()
print(intraday_data.head())

# Get historical data
end_date = datetime.now()
start_date = end_date.replace(month=end_date.month-3)
historical_data = ticker.get_historical_data(start_date=start_date, end_date=end_date)
print(historical_data.head())
```

## Examples

Check out the `examples/` directory for more usage examples:
- `basic_usage.py`: Basic data fetching
- `historical_analysis.py`: Historical data analysis
- `multiple_symbols.py`: Working with multiple symbols

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run specific test
pytest tests/test_hbl.py -v
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Uses PSX website data
- Built with pandas and requests 