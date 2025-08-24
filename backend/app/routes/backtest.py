from flask import request, jsonify, current_app
import pandas as pd
import uuid
import json
import os
from datetime import datetime, timedelta
from . import api_bp
from ..strategies import get_strategy_class
from ..utils.cache import cache
from ..utils.storage import save_backtest_result, get_backtest_result
from ..utils.data import get_stock_data

@api_bp.route('/backtest', methods=['POST'])
def run_backtest():
    """
    Run a backtest for a specific strategy on selected stocks
    
    Request body:
    {
        "strategy_id": "bull_hook",
        "stock_list_id": "nifty_50",
        "stocks": ["RELIANCE.NS", "TCS.NS", ...],  # Optional, if not provided, all stocks in the list will be used
        "start_date": "2020-01-01",
        "end_date": "2023-12-31",
        "initial_capital": 100000,
        "parameters": {
            "volume_threshold": 120,
            "use_stoch_rsi": true,
            "use_macd": false,
            "risk_per_trade": 1.0
        }
    }
    
    Returns:
        JSON response with backtest results
    """
    data = request.json
    
    # Validate required fields
    required_fields = ['strategy_id', 'stock_list_id', 'start_date', 'end_date', 'initial_capital']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Extract parameters
    strategy_id = data['strategy_id']
    stock_list_id = data['stock_list_id']
    start_date = data['start_date']
    end_date = data['end_date']
    initial_capital = data['initial_capital']
    parameters = data.get('parameters', {})
    stocks = data.get('stocks', [])
    
    # Generate a unique ID for this backtest
    backtest_id = str(uuid.uuid4())
    
    try:
        # Check if we have cached results for this exact backtest configuration
        cache_key = f"backtest_{strategy_id}_{stock_list_id}_{start_date}_{end_date}_{initial_capital}_{json.dumps(parameters, sort_keys=True)}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return jsonify({
                'backtest_id': cached_result['backtest_id'],
                'results': cached_result['results'],
                'cached': True
            })
        
        # Get the strategy class
        strategy_class = get_strategy_class(strategy_id)
        
        # If stocks is empty, get all stocks from the stock list
        if not stocks:
            # This would call the get_stock_list function from stock_lists.py
            # For simplicity, we'll just use a placeholder here
            if stock_list_id == 'nifty_50':
                # In a real application, this would fetch the actual Nifty 50 stocks
                stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]
            else:
                return jsonify({'error': 'Invalid stock list ID'}), 400
        
        # Initialize the strategy with parameters
        strategy = strategy_class(**parameters)
        
        # Fetch historical data for the stocks
        stock_data = {}
        for symbol in stocks:
            try:
                # Get historical data
                df = get_stock_data(symbol, start_date, end_date)
                if not df.empty:
                    stock_data[symbol] = df
            except Exception as e:
                current_app.logger.error(f"Error fetching data for {symbol}: {str(e)}")
        
        # Run the backtest
        results = strategy.backtest(stock_data, initial_capital)
        
        # Save the results
        save_backtest_result(backtest_id, {
            'strategy_id': strategy_id,
            'stock_list_id': stock_list_id,
            'stocks': stocks,
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': initial_capital,
            'parameters': parameters,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
        # Cache the results
        cache.set(cache_key, {
            'backtest_id': backtest_id,
            'results': results
        })
        
        return jsonify({
            'backtest_id': backtest_id,
            'results': results,
            'cached': False
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        current_app.logger.error(f"Backtest error: {str(e)}")
        return jsonify({'error': 'An error occurred during backtesting'}), 500


@api_bp.route('/backtest/<backtest_id>', methods=['GET'])
def get_backtest(backtest_id):
    """
    Get results for a specific backtest
    
    Args:
        backtest_id: ID of the backtest
        
    Returns:
        JSON response with backtest results
    """
    try:
        # Get the backtest results
        backtest = get_backtest_result(backtest_id)
        
        if not backtest:
            return jsonify({'error': 'Backtest not found'}), 404
        
        return jsonify(backtest)
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving backtest: {str(e)}")
        return jsonify({'error': 'An error occurred while retrieving the backtest'}), 500


@api_bp.route('/backtest/history', methods=['GET'])
def get_backtest_history():
    """
    Get history of backtests for the current user
    
    Returns:
        JSON response with backtest history
    """
    # In a real application, this would filter by user ID
    # For now, we'll just return all backtests
    
    try:
        # This is a placeholder. In a real application, you would query the database
        # or storage for the user's backtest history
        backtests = [
            {
                'id': '123e4567-e89b-12d3-a456-426614174000',
                'strategy_id': 'bull_hook',
                'stock_list_id': 'nifty_50',
                'start_date': '2020-01-01',
                'end_date': '2023-12-31',
                'timestamp': '2023-01-15T14:30:00',
                'summary': {
                    'total_return': 87.5,
                    'win_rate': 68.2,
                    'profit_factor': 2.94
                }
            },
            {
                'id': '223e4567-e89b-12d3-a456-426614174001',
                'strategy_id': 'bull_hook',
                'stock_list_id': 'nifty_next_50',
                'start_date': '2021-01-01',
                'end_date': '2023-12-31',
                'timestamp': '2023-01-16T10:15:00',
                'summary': {
                    'total_return': 62.3,
                    'win_rate': 64.7,
                    'profit_factor': 2.51
                }
            }
        ]
        
        return jsonify({'backtests': backtests})
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving backtest history: {str(e)}")
        return jsonify({'error': 'An error occurred while retrieving backtest history'}), 500