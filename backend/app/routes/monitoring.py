from flask import request, jsonify, current_app
import pandas as pd
from datetime import datetime, timedelta
import uuid
from . import api_bp
from ..strategies import get_strategy_class
from ..utils.data import get_stock_data
from ..utils.cache import cache

@api_bp.route('/monitoring/scan', methods=['POST'])
def scan_for_opportunities():
    """
    Scan for trading opportunities using a specific strategy
    
    Request body:
    {
        "strategy_id": "bull_hook",
        "stock_list_id": "nifty_50",
        "stocks": ["RELIANCE.NS", "TCS.NS", ...],  # Optional, if not provided, all stocks in the list will be used
        "parameters": {
            "volume_threshold": 120,
            "use_stoch_rsi": true,
            "use_macd": false,
            "risk_per_trade": 1.0
        }
    }
    
    Returns:
        JSON response with trading opportunities
    """
    data = request.json
    
    # Validate required fields
    required_fields = ['strategy_id', 'stock_list_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Extract parameters
    strategy_id = data['strategy_id']
    stock_list_id = data['stock_list_id']
    parameters = data.get('parameters', {})
    stocks = data.get('stocks', [])
    
    try:
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
        
        # Calculate the start date (e.g., 100 days ago for sufficient historical data)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=100)).strftime('%Y-%m-%d')
        
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
        
        # Scan for opportunities
        opportunities = strategy.scan_for_opportunities(stock_data)
        
        # Generate a unique ID for this scan
        scan_id = str(uuid.uuid4())
        
        # In a real application, you would save the scan results to the database
        
        return jsonify({
            'scan_id': scan_id,
            'timestamp': datetime.now().isoformat(),
            'opportunities': opportunities
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        current_app.logger.error(f"Scan error: {str(e)}")
        return jsonify({'error': 'An error occurred during scanning'}), 500


@api_bp.route('/monitoring/setup', methods=['POST'])
def setup_monitoring():
    """
    Set up daily monitoring for trading opportunities
    
    Request body:
    {
        "strategy_id": "bull_hook",
        "stock_list_id": "nifty_50",
        "stocks": ["RELIANCE.NS", "TCS.NS", ...],  # Optional, if not provided, all stocks in the list will be used
        "parameters": {
            "volume_threshold": 120,
            "use_stoch_rsi": true,
            "use_macd": false,
            "risk_per_trade": 1.0
        },
        "notification_email": "user@example.com",  # Optional
        "notification_time": "16:30"  # Optional, time in 24-hour format
    }
    
    Returns:
        JSON response with monitoring setup details
    """
    data = request.json
    
    # Validate required fields
    required_fields = ['strategy_id', 'stock_list_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Extract parameters
    strategy_id = data['strategy_id']
    stock_list_id = data['stock_list_id']
    parameters = data.get('parameters', {})
    stocks = data.get('stocks', [])
    notification_email = data.get('notification_email')
    notification_time = data.get('notification_time', '16:30')
    
    try:
        # Generate a unique ID for this monitoring setup
        monitoring_id = str(uuid.uuid4())
        
        # In a real application, you would save the monitoring setup to the database
        # and set up a scheduled task to run the scan daily
        
        # For now, we'll just return a success response
        return jsonify({
            'monitoring_id': monitoring_id,
            'strategy_id': strategy_id,
            'stock_list_id': stock_list_id,
            'stocks_count': len(stocks) if stocks else 'all',
            'notification_email': notification_email,
            'notification_time': notification_time,
            'status': 'active',
            'message': 'Monitoring setup successful. You will receive notifications when trading opportunities are found.'
        })
    
    except Exception as e:
        current_app.logger.error(f"Monitoring setup error: {str(e)}")
        return jsonify({'error': 'An error occurred during monitoring setup'}), 500


@api_bp.route('/monitoring', methods=['GET'])
def get_monitoring_setups():
    """
    Get all monitoring setups for the current user
    
    Returns:
        JSON response with monitoring setups
    """
    # In a real application, this would filter by user ID
    # For now, we'll just return a placeholder
    
    try:
        # This is a placeholder. In a real application, you would query the database
        # for the user's monitoring setups
        setups = [
            {
                'id': '123e4567-e89b-12d3-a456-426614174000',
                'strategy_id': 'bull_hook',
                'stock_list_id': 'nifty_50',
                'stocks_count': 'all',
                'notification_email': 'user@example.com',
                'notification_time': '16:30',
                'status': 'active',
                'created_at': '2023-01-15T14:30:00'
            }
        ]
        
        return jsonify({'monitoring_setups': setups})
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving monitoring setups: {str(e)}")
        return jsonify({'error': 'An error occurred while retrieving monitoring setups'}), 500


@api_bp.route('/monitoring/<monitoring_id>', methods=['DELETE'])
def delete_monitoring(monitoring_id):
    """
    Delete a monitoring setup
    
    Args:
        monitoring_id: ID of the monitoring setup
        
    Returns:
        JSON response with deletion status
    """
    try:
        # In a real application, you would delete the monitoring setup from the database
        # and cancel any scheduled tasks
        
        # For now, we'll just return a success response
        return jsonify({
            'message': f'Monitoring setup {monitoring_id} deleted successfully'
        })
    
    except Exception as e:
        current_app.logger.error(f"Error deleting monitoring setup: {str(e)}")
        return jsonify({'error': 'An error occurred while deleting the monitoring setup'}), 500


@api_bp.route('/monitoring/alerts', methods=['GET'])
def get_alerts():
    """
    Get recent alerts for the current user
    
    Returns:
        JSON response with alerts
    """
    # In a real application, this would filter by user ID
    # For now, we'll just return a placeholder
    
    try:
        # This is a placeholder. In a real application, you would query the database
        # for the user's alerts
        alerts = [
            {
                'id': '123e4567-e89b-12d3-a456-426614174000',
                'strategy_id': 'bull_hook',
                'stock': 'RELIANCE.NS',
                'signal_type': 'buy',
                'entry_price': 2500.75,
                'stop_loss': 2450.25,
                'target1': 2575.50,
                'target2': 2625.25,
                'target3': 2725.00,
                'timestamp': '2023-01-15T16:30:00',
                'status': 'new'
            }
        ]
        
        return jsonify({'alerts': alerts})
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving alerts: {str(e)}")
        return jsonify({'error': 'An error occurred while retrieving alerts'}), 500