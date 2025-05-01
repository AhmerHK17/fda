"""
Authentication module for PSX data sources including TradingView integration.
"""
import os
import requests
from typing import Optional, Dict, Any
from tradingview_ta import TA_Handler
from .exceptions import PSXConnectionError, PSXRequestError

class TVSession:
    """
    Manages TradingView authentication and session handling.
    """
    def __init__(self):
        self.session = requests.Session()
        self.authenticated = False
        self.handler: Optional[TA_Handler] = None
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        
    def authenticate(self, username: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        Authenticate with TradingView. If credentials are not provided,
        will attempt to use environment variables TV_USERNAME and TV_PASSWORD.
        
        Args:
            username: TradingView username (optional)
            password: TradingView password (optional)
            
        Raises:
            PSXConnectionError: If connection fails
            PSXRequestError: If authentication fails
        """
        try:
            # Get credentials from environment if not provided
            self._username = username or os.getenv('TV_USERNAME')
            self._password = password or os.getenv('TV_PASSWORD')
            
            if not self._username or not self._password:
                raise PSXRequestError(
                    "TradingView credentials not provided. Either pass them to authenticate() "
                    "or set TV_USERNAME and TV_PASSWORD environment variables."
                )
            
            # Initialize TA Handler with default settings
            # We'll configure it per request since symbol changes
            self.handler = TA_Handler(
                symbol="DUMMY",
                exchange="PSX",
                screener="pakistan",
                interval="1d"
            )
            
            # Test authentication by trying to get data
            # This will raise an exception if authentication fails
            self.handler.get_analysis()
            
            self.authenticated = True
            
        except Exception as e:
            self.authenticated = False
            if isinstance(e, requests.exceptions.RequestException):
                raise PSXConnectionError(f"Failed to connect to TradingView: {str(e)}")
            else:
                raise PSXRequestError(f"TradingView authentication failed: {str(e)}")
    
    def get_handler(self, symbol: str) -> TA_Handler:
        """
        Get a configured TA_Handler for a specific symbol.
        
        Args:
            symbol: Stock symbol to configure handler for
            
        Returns:
            Configured TA_Handler instance
            
        Raises:
            PSXRequestError: If not authenticated
        """
        if not self.authenticated or not self.handler:
            raise PSXRequestError("TradingView session not authenticated")
            
        self.handler.symbol = symbol
        return self.handler
            
    def get_session(self) -> requests.Session:
        """
        Get the authenticated session.
        
        Returns:
            Authenticated requests.Session object
            
        Raises:
            PSXRequestError: If not authenticated
        """
        if not self.authenticated:
            raise PSXRequestError("TradingView session not authenticated")
        return self.session 