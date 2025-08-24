from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from datetime import datetime

class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    @classmethod
    def get_default_parameters(cls):
        """
        Get default parameters for the strategy
        
        Returns:
            Dictionary of default parameters
        """
        return {}
    
    @abstractmethod
    def generate_signals(self, data):
        """
        Generate trading signals for a single stock
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with signals
        """
        pass
    
    @abstractmethod
    def backtest(self, stock_data, initial_capital):
        """
        Run a backtest for the strategy
        
        Args:
            stock_data: Dictionary mapping stock symbols to DataFrames with OHLCV data
            initial_capital: Initial capital for the backtest
            
        Returns:
            Dictionary with backtest results
        """
        pass
    
    @abstractmethod
    def scan_for_opportunities(self, stock_data):
        """
        Scan for trading opportunities
        
        Args:
            stock_data: Dictionary mapping stock symbols to DataFrames with OHLCV data
            
        Returns:
            List of trading opportunities
        """
        pass
    
    def calculate_position_size(self, capital, entry_price, stop_loss, risk_per_trade):
        """
        Calculate position size based on risk
        
        Args:
            capital: Available capital
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_per_trade: Risk per trade as a percentage of capital
            
        Returns:
            Number of shares to buy
        """
        risk_amount = capital * (risk_per_trade / 100)
        price_risk = entry_price - stop_loss
        
        if price_risk <= 0:
            return 0
        
        shares = risk_amount / price_risk
        
        # Round down to nearest whole number
        return int(shares)
    
    def calculate_returns(self, portfolio_values):
        """
        Calculate return metrics
        
        Args:
            portfolio_values: Series of portfolio values
            
        Returns:
            Dictionary with return metrics
        """
        # Calculate daily returns
        daily_returns = portfolio_values.pct_change().dropna()
        
        # Calculate cumulative returns
        cumulative_returns = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) - 1
        
        # Calculate annualized return
        days = (portfolio_values.index[-1] - portfolio_values.index[0]).days
        years = days / 365.25
        annualized_return = (1 + cumulative_returns) ** (1 / years) - 1 if years > 0 else 0
        
        # Calculate volatility
        volatility = daily_returns.std() * np.sqrt(252)
        
        # Calculate Sharpe ratio (assuming risk-free rate of 0)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # Calculate drawdown
        running_max = portfolio_values.cummax()
        drawdown = (portfolio_values - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return {
            'total_return': cumulative_returns * 100,
            'annualized_return': annualized_return * 100,
            'volatility': volatility * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown * 100
        }
    
    def calculate_trade_metrics(self, trades):
        """
        Calculate trade metrics
        
        Args:
            trades: List of trade dictionaries
            
        Returns:
            Dictionary with trade metrics
        """
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'avg_trade': 0,
                'avg_bars_held': 0
            }
        
        # Calculate metrics
        total_trades = len(trades)
        winning_trades = sum(1 for trade in trades if trade['pnl'] > 0)
        losing_trades = sum(1 for trade in trades if trade['pnl'] <= 0)
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        winning_pnl = [trade['pnl'] for trade in trades if trade['pnl'] > 0]
        losing_pnl = [trade['pnl'] for trade in trades if trade['pnl'] <= 0]
        
        avg_win = sum(winning_pnl) / winning_trades if winning_trades > 0 else 0
        avg_loss = sum(losing_pnl) / losing_trades if losing_trades > 0 else 0
        
        profit_factor = abs(sum(winning_pnl) / sum(losing_pnl)) if sum(losing_pnl) != 0 else float('inf')
        
        avg_trade = sum(trade['pnl'] for trade in trades) / total_trades
        
        avg_bars_held = sum(trade['bars_held'] for trade in trades) / total_trades
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate * 100,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'avg_trade': avg_trade,
            'avg_bars_held': avg_bars_held
        }