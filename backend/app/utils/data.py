import pandas as pd
import numpy as np
import yfinance as yf
from flask import current_app
from .cache import cache

@cache.memoize(timeout=86400)  # Cache for 24 hours
def get_stock_data(symbol, start_date, end_date):
    """
    Get historical stock data from Yahoo Finance
    
    Args:
        symbol: Stock symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        DataFrame with OHLCV data
    """
    try:
        # Download data from Yahoo Finance
        data = yf.download(symbol, start=start_date, end=end_date)
        
        # Check if data is empty
        if data.empty:
            current_app.logger.warning(f"No data found for {symbol}")
            return pd.DataFrame()
        
        return data
    
    except Exception as e:
        current_app.logger.error(f"Error fetching data for {symbol}: {str(e)}")
        return pd.DataFrame()


def get_market_data(start_date, end_date, index='^NSEI'):
    """
    Get market index data
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        index: Market index symbol (default: ^NSEI for Nifty 50)
        
    Returns:
        DataFrame with OHLCV data
    """
    return get_stock_data(index, start_date, end_date)


def get_sector_performance(stocks, start_date, end_date, sectors):
    """
    Calculate sector performance
    
    Args:
        stocks: List of stock symbols
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        sectors: Dictionary mapping stock symbols to sectors
        
    Returns:
        Dictionary with sector performance
    """
    # Group stocks by sector
    sector_stocks = {}
    for symbol in stocks:
        sector = sectors.get(symbol, 'Other')
        if sector not in sector_stocks:
            sector_stocks[sector] = []
        sector_stocks[sector].append(symbol)
    
    # Calculate sector performance
    sector_performance = {}
    
    for sector, symbols in sector_stocks.items():
        # Get data for all stocks in the sector
        sector_data = {}
        for symbol in symbols:
            data = get_stock_data(symbol, start_date, end_date)
            if not data.empty:
                sector_data[symbol] = data
        
        if not sector_data:
            continue
        
        # Calculate sector index (equal-weighted)
        first_symbol = list(sector_data.keys())[0]
        index_dates = sector_data[first_symbol].index
        
        sector_index = pd.DataFrame(index=index_dates)
        sector_index['Close'] = 0
        
        for symbol, data in sector_data.items():
            # Normalize to 100 at the start
            normalized = data['Close'] / data['Close'].iloc[0] * 100
            # Reindex to match the index dates
            normalized = normalized.reindex(index_dates)
            # Add to the sector index
            sector_index['Close'] += normalized / len(sector_data)
        
        # Calculate returns
        sector_index['Returns'] = sector_index['Close'].pct_change()
        
        # Calculate performance metrics
        total_return = (sector_index['Close'].iloc[-1] / sector_index['Close'].iloc[0]) - 1
        annualized_return = (1 + total_return) ** (252 / len(sector_index)) - 1
        volatility = sector_index['Returns'].std() * np.sqrt(252)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # Store sector performance
        sector_performance[sector] = {
            'total_return': total_return * 100,
            'annualized_return': annualized_return * 100,
            'volatility': volatility * 100,
            'sharpe_ratio': sharpe_ratio,
            'stocks_count': len(symbols)
        }
    
    return sector_performance