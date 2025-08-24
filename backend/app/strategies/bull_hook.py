import pandas as pd
import numpy as np
from datetime import datetime
from .base import BaseStrategy

class BullHookStrategy(BaseStrategy):
    """
    Bull Hook trading strategy implementation
    
    The Bull Hook pattern is characterized by:
    1. The open is above the previous day's high
    2. The close is below the previous day's close
    3. The daily range is narrower than the previous day's range
    """
    
    def __init__(self, volume_threshold=120, use_stoch_rsi=True, use_macd=False, risk_per_trade=1.0):
        """
        Initialize the Bull Hook strategy
        
        Args:
            volume_threshold: Minimum volume as percentage of 20-day average
            use_stoch_rsi: Whether to use Stochastic RSI crossover as a filter
            use_macd: Whether to use MACD histogram divergence as a filter
            risk_per_trade: Percentage of portfolio to risk per trade
        """
        self.volume_threshold = volume_threshold
        self.use_stoch_rsi = use_stoch_rsi
        self.use_macd = use_macd
        self.risk_per_trade = risk_per_trade
    
    @classmethod
    def get_default_parameters(cls):
        """
        Get default parameters for the strategy
        
        Returns:
            Dictionary of default parameters
        """
        return {
            'volume_threshold': 120,
            'use_stoch_rsi': True,
            'use_macd': False,
            'risk_per_trade': 1.0
        }
    
    def calculate_indicators(self, data):
        """
        Calculate technical indicators for the strategy
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with indicators
        """
        df = data.copy()
        
        # Calculate ATR (Average True Range)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR'] = true_range.rolling(14).mean()
        
        # Calculate daily range
        df['Daily_Range'] = df['High'] - df['Low']
        
        # Calculate volume condition
        df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        df['Volume_Condition'] = df['Volume_Ratio'] > (self.volume_threshold / 100)
        
        # Calculate RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        if self.use_stoch_rsi:
            # Calculate Stochastic RSI
            stoch_window = 14
            rsi_values = df['RSI'].values
            
            # Initialize arrays for %K and %D
            k_values = np.zeros_like(rsi_values)
            d_values = np.zeros_like(rsi_values)
            
            # Calculate %K and %D
            for i in range(stoch_window, len(rsi_values)):
                window = rsi_values[i-stoch_window+1:i+1]
                if np.max(window) - np.min(window) != 0:
                    k_values[i] = 100 * (rsi_values[i] - np.min(window)) / (np.max(window) - np.min(window))
                else:
                    k_values[i] = 0
            
            # Calculate %D (3-period SMA of %K)
            for i in range(stoch_window + 2, len(k_values)):
                d_values[i] = np.mean(k_values[i-2:i+1])
            
            df['StochRSI_K'] = k_values
            df['StochRSI_D'] = d_values
            
            # Calculate StochRSI crossover
            df['StochRSI_Crossover'] = ((df['StochRSI_K'] > df['StochRSI_D']) & 
                                        (df['StochRSI_K'].shift() <= df['StochRSI_D'].shift()))
        
        if self.use_macd:
            # Calculate MACD
            df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA12'] - df['EMA26']
            df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Hist'] = df['MACD'] - df['Signal']
            
            # Calculate MACD histogram divergence (simple implementation)
            df['MACD_Divergence'] = ((df['Close'] < df['Close'].shift()) & 
                                     (df['MACD_Hist'] > df['MACD_Hist'].shift()))
        
        # Calculate moving averages for trend determination
        df['SMA20'] = df['Close'].rolling(20).mean()
        df['SMA50'] = df['Close'].rolling(50).mean()
        
        # Determine market trend
        df['Market_Trend'] = 'Sideways'
        df.loc[df['SMA20'] > df['SMA50'], 'Market_Trend'] = 'Uptrend'
        df.loc[df['SMA20'] < df['SMA50'], 'Market_Trend'] = 'Downtrend'
        
        return df
    
    def generate_signals(self, data):
        """
        Generate trading signals for a single stock
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with signals
        """
        df = self.calculate_indicators(data)
        
        # Initialize signal column
        df['Signal'] = 0
        
        # Identify Bull Hook patterns
        for i in range(2, len(df)):
            # Get current and previous day's data
            current_day = df.iloc[i]
            prev_day = df.iloc[i-1]
            
            # Check for Bull Hook pattern
            bull_hook_condition = (
                current_day['Open'] > prev_day['High'] and
                current_day['Close'] < prev_day['Close'] and
                current_day['Daily_Range'] < prev_day['Daily_Range']
            )
            
            if bull_hook_condition:
                # Check complementary indicators
                volume_condition = current_day['Volume_Condition']
                
                stoch_rsi_condition = False
                if self.use_stoch_rsi:
                    stoch_rsi_condition = current_day['StochRSI_Crossover']
                
                macd_condition = False
                if self.use_macd:
                    macd_condition = current_day['MACD_Divergence']
                
                # Generate signal if pattern and at least one condition is met
                if volume_condition or (self.use_stoch_rsi and stoch_rsi_condition) or (self.use_macd and macd_condition):
                    df.loc[df.index[i], 'Signal'] = 1
        
        return df
    
    def backtest(self, stock_data, initial_capital):
        """
        Run a backtest for the strategy
        
        Args:
            stock_data: Dictionary mapping stock symbols to DataFrames with OHLCV data
            initial_capital: Initial capital for the backtest
            
        Returns:
            Dictionary with backtest results
        """
        # Initialize portfolio
        portfolio = pd.DataFrame(index=pd.DatetimeIndex([]))
        portfolio['Cash'] = initial_capital
        portfolio['Equity'] = 0
        portfolio['Total'] = initial_capital
        
        # Initialize trades list
        trades = []
        
        # Process each stock
        for symbol, data in stock_data.items():
            # Generate signals
            df = self.generate_signals(data)
            
            # Skip if no signals
            if df['Signal'].sum() == 0:
                continue
            
            # Get all dates from the data
            all_dates = df.index
            
            # Update portfolio DataFrame to include all dates
            portfolio = portfolio.reindex(portfolio.index.union(all_dates))
            portfolio = portfolio.fillna(method='ffill')
            
            # Initialize position tracking
            position = 0
            entry_price = 0
            entry_date = None
            entry_index = 0
            
            # Loop through the data
            for i in range(len(df)):
                current_date = df.index[i]
                
                # Check for entry signal
                if df['Signal'].iloc[i] == 1 and position == 0:
                    # Calculate entry price, stop loss, and targets
                    entry_price = df['Close'].iloc[i]
                    stop_loss = entry_price - 1.5 * df['ATR'].iloc[i]
                    target1 = entry_price + 2.0 * df['ATR'].iloc[i]
                    target2 = entry_price + 3.0 * df['ATR'].iloc[i]
                    target3 = entry_price + 5.0 * df['ATR'].iloc[i]
                    
                    # Calculate position size
                    available_capital = portfolio.loc[current_date, 'Cash']
                    risk_amount = available_capital * (self.risk_per_trade / 100)
                    price_risk = entry_price - stop_loss
                    
                    if price_risk <= 0:
                        continue
                    
                    shares = int(risk_amount / price_risk)
                    
                    if shares <= 0:
                        continue
                    
                    # Enter position
                    position = shares
                    entry_date = current_date
                    entry_index = i
                    
                    # Update portfolio
                    portfolio.loc[current_date, 'Cash'] -= entry_price * position
                    portfolio.loc[current_date, 'Equity'] += entry_price * position
                
                # Check for exit conditions if in a position
                elif position > 0:
                    current_price = df['Close'].iloc[i]
                    
                    # Check if stop loss is hit
                    if current_price <= stop_loss:
                        # Exit position
                        pnl = (current_price - entry_price) * position
                        
                        # Update portfolio
                        portfolio.loc[current_date, 'Cash'] += current_price * position
                        portfolio.loc[current_date, 'Equity'] -= entry_price * position
                        
                        # Record trade
                        trades.append({
                            'symbol': symbol,
                            'entry_date': entry_date,
                            'exit_date': current_date,
                            'entry_price': entry_price,
                            'exit_price': current_price,
                            'shares': position,
                            'pnl': pnl,
                            'pnl_percent': (current_price - entry_price) / entry_price * 100,
                            'exit_reason': 'Stop Loss',
                            'bars_held': i - entry_index
                        })
                        
                        # Reset position
                        position = 0
                    
                    # Check if target 1 is hit (exit 50%)
                    elif current_price >= target1 and position > 0:
                        # Calculate shares to exit
                        shares_to_exit = position // 2
                        
                        if shares_to_exit > 0:
                            # Exit partial position
                            pnl = (current_price - entry_price) * shares_to_exit
                            
                            # Update portfolio
                            portfolio.loc[current_date, 'Cash'] += current_price * shares_to_exit
                            portfolio.loc[current_date, 'Equity'] -= entry_price * shares_to_exit
                            
                            # Record trade
                            trades.append({
                                'symbol': symbol,
                                'entry_date': entry_date,
                                'exit_date': current_date,
                                'entry_price': entry_price,
                                'exit_price': current_price,
                                'shares': shares_to_exit,
                                'pnl': pnl,
                                'pnl_percent': (current_price - entry_price) / entry_price * 100,
                                'exit_reason': 'Target 1',
                                'bars_held': i - entry_index
                            })
                            
                            # Update position
                            position -= shares_to_exit
                            
                            # Move stop loss to breakeven
                            stop_loss = entry_price
                    
                    # Check if target 2 is hit (exit 50% of remaining)
                    elif current_price >= target2 and position > 0:
                        # Calculate shares to exit
                        shares_to_exit = position // 2
                        
                        if shares_to_exit > 0:
                            # Exit partial position
                            pnl = (current_price - entry_price) * shares_to_exit
                            
                            # Update portfolio
                            portfolio.loc[current_date, 'Cash'] += current_price * shares_to_exit
                            portfolio.loc[current_date, 'Equity'] -= entry_price * shares_to_exit
                            
                            # Record trade
                            trades.append({
                                'symbol': symbol,
                                'entry_date': entry_date,
                                'exit_date': current_date,
                                'entry_price': entry_price,
                                'exit_price': current_price,
                                'shares': shares_to_exit,
                                'pnl': pnl,
                                'pnl_percent': (current_price - entry_price) / entry_price * 100,
                                'exit_reason': 'Target 2',
                                'bars_held': i - entry_index
                            })
                            
                            # Update position
                            position -= shares_to_exit
                    
                    # Check if target 3 is hit (exit remaining)
                    elif current_price >= target3 and position > 0:
                        # Exit remaining position
                        pnl = (current_price - entry_price) * position
                        
                        # Update portfolio
                        portfolio.loc[current_date, 'Cash'] += current_price * position
                        portfolio.loc[current_date, 'Equity'] -= entry_price * position
                        
                        # Record trade
                        trades.append({
                            'symbol': symbol,
                            'entry_date': entry_date,
                            'exit_date': current_date,
                            'entry_price': entry_price,
                            'exit_price': current_price,
                            'shares': position,
                            'pnl': pnl,
                            'pnl_percent': (current_price - entry_price) / entry_price * 100,
                            'exit_reason': 'Target 3',
                            'bars_held': i - entry_index
                        })
                        
                        # Reset position
                        position = 0
                    
                    # Check for time-based exit (after 10 days)
                    elif (i - entry_index) >= 10 and position > 0:
                        # Exit position
                        pnl = (current_price - entry_price) * position
                        
                        # Update portfolio
                        portfolio.loc[current_date, 'Cash'] += current_price * position
                        portfolio.loc[current_date, 'Equity'] -= entry_price * position
                        
                        # Record trade
                        trades.append({
                            'symbol': symbol,
                            'entry_date': entry_date,
                            'exit_date': current_date,
                            'entry_price': entry_price,
                            'exit_price': current_price,
                            'shares': position,
                            'pnl': pnl,
                            'pnl_percent': (current_price - entry_price) / entry_price * 100,
                            'exit_reason': 'Time Exit',
                            'bars_held': i - entry_index
                        })
                        
                        # Reset position
                        position = 0
            
            # Close any remaining position at the end of the data
            if position > 0:
                current_date = df.index[-1]
                current_price = df['Close'].iloc[-1]
                
                # Exit position
                pnl = (current_price - entry_price) * position
                
                # Update portfolio
                portfolio.loc[current_date, 'Cash'] += current_price * position
                portfolio.loc[current_date, 'Equity'] -= entry_price * position
                
                # Record trade
                trades.append({
                    'symbol': symbol,
                    'entry_date': entry_date,
                    'exit_date': current_date,
                    'entry_price': entry_price,
                    'exit_price': current_price,
                    'shares': position,
                    'pnl': pnl,
                    'pnl_percent': (current_price - entry_price) / entry_price * 100,
                    'exit_reason': 'End of Data',
                    'bars_held': len(df) - 1 - entry_index
                })
        
        # Calculate total portfolio value
        portfolio['Total'] = portfolio['Cash'] + portfolio['Equity']
        
        # Fill any missing values
        portfolio = portfolio.fillna(method='ffill')
        
        # Calculate return metrics
        return_metrics = self.calculate_returns(portfolio['Total'])
        
        # Calculate trade metrics
        trade_metrics = self.calculate_trade_metrics(trades)
        
        # Prepare results
        results = {
            'portfolio': portfolio.to_dict(orient='records'),
            'trades': trades,
            'return_metrics': return_metrics,
            'trade_metrics': trade_metrics,
            'summary': {
                'initial_capital': initial_capital,
                'final_capital': portfolio['Total'].iloc[-1],
                'total_return': return_metrics['total_return'],
                'annualized_return': return_metrics['annualized_return'],
                'sharpe_ratio': return_metrics['sharpe_ratio'],
                'max_drawdown': return_metrics['max_drawdown'],
                'win_rate': trade_metrics['win_rate'],
                'profit_factor': trade_metrics['profit_factor'],
                'total_trades': trade_metrics['total_trades']
            }
        }
        
        return results
    
    def scan_for_opportunities(self, stock_data):
        """
        Scan for trading opportunities
        
        Args:
            stock_data: Dictionary mapping stock symbols to DataFrames with OHLCV data
            
        Returns:
            List of trading opportunities
        """
        opportunities = []
        
        for symbol, data in stock_data.items():
            # Generate signals
            df = self.generate_signals(data)
            
            # Check the last day for a signal
            if len(df) > 0 and df['Signal'].iloc[-1] == 1:
                # Get the last day's data
                last_day = df.iloc[-1]
                
                # Calculate entry, stop loss, and targets
                entry_price = last_day['Close']
                stop_loss = entry_price - 1.5 * last_day['ATR']
                target1 = entry_price + 2.0 * last_day['ATR']
                target2 = entry_price + 3.0 * last_day['ATR']
                target3 = entry_price + 5.0 * last_day['ATR']
                
                # Calculate risk-reward ratio
                risk = entry_price - stop_loss
                reward = ((target1 - entry_price) * 0.5 + 
                          (target2 - entry_price) * 0.25 + 
                          (target3 - entry_price) * 0.25)
                risk_reward = reward / risk if risk > 0 else 0
                
                # Check which conditions are met
                conditions_met = []
                
                if last_day['Volume_Condition']:
                    conditions_met.append('Volume > 120% of 20-day average')
                
                if self.use_stoch_rsi and last_day['StochRSI_Crossover']:
                    conditions_met.append('Stochastic RSI Crossover')
                
                if self.use_macd and last_day['MACD_Divergence']:
                    conditions_met.append('MACD Histogram Divergence')
                
                # Add opportunity
                opportunities.append({
                    'symbol': symbol,
                    'date': last_day.name.strftime('%Y-%m-%d'),
                    'pattern': 'Bull Hook',
                    'entry_price': float(entry_price),
                    'stop_loss': float(stop_loss),
                    'target1': float(target1),
                    'target2': float(target2),
                    'target3': float(target3),
                    'risk_reward': float(risk_reward),
                    'market_trend': last_day['Market_Trend'],
                    'conditions_met': conditions_met,
                    'confidence': len(conditions_met) / 3 * 100  # Confidence based on number of conditions met
                })
        
        # Sort opportunities by confidence (descending)
        opportunities = sorted(opportunities, key=lambda x: x['confidence'], reverse=True)
        
        return opportunities