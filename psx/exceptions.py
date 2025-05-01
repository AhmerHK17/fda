class PSXError(Exception):
    """Base exception for PSX library"""
    pass

class PSXConnectionError(PSXError):
    """Raised when there's an error connecting to PSX APIs"""
    pass

class PSXDataError(PSXError):
    """Raised when there's an error with the data received"""
    pass

class PSXSymbolError(PSXError):
    """Raised when there's an error with the stock symbol"""
    pass

class PSXRequestError(PSXError):
    """Raised when there is an error with the API request (e.g., authentication, invalid symbol)."""
    pass 