from flask import request, jsonify, current_app
from . import api_bp
from ..strategies import get_strategy_class
from ..utils.cache import cache

@api_bp.route('/strategies', methods=['GET'])
def get_strategies():
    """
    Get available trading strategies
    
    Returns:
        JSON response with available strategies
    """
    strategies = [
        {
            'id': 'bull_hook',
            'name': 'Bull Hook Strategy',
            'description': 'A strategy based on the Bull Hook pattern, which identifies potential reversals.',
            'parameters': [
                {
                    'id': 'volume_threshold',
                    'name': 'Volume Threshold',
                    'description': 'Minimum volume as percentage of 20-day average',
                    'type': 'number',
                    'default': 120,
                    'min': 100,
                    'max': 200
                },
                {
                    'id': 'use_stoch_rsi',
                    'name': 'Use Stochastic RSI',
                    'description': 'Use Stochastic RSI crossover as a filter',
                    'type': 'boolean',
                    'default': True
                },
                {
                    'id': 'use_macd',
                    'name': 'Use MACD Divergence',
                    'description': 'Use MACD histogram divergence as a filter',
                    'type': 'boolean',
                    'default': False
                },
                {
                    'id': 'risk_per_trade',
                    'name': 'Risk Per Trade',
                    'description': 'Percentage of portfolio to risk per trade',
                    'type': 'number',
                    'default': 1.0,
                    'min': 0.1,
                    'max': 5.0
                }
            ]
        }
        # Additional strategies would be added here
    ]
    
    return jsonify({'strategies': strategies})


@api_bp.route('/strategies/<strategy_id>', methods=['GET'])
def get_strategy(strategy_id):
    """
    Get details for a specific strategy
    
    Args:
        strategy_id: ID of the strategy
        
    Returns:
        JSON response with strategy details
    """
    if strategy_id == 'bull_hook':
        strategy = {
            'id': 'bull_hook',
            'name': 'Bull Hook Strategy',
            'description': 'A strategy based on the Bull Hook pattern, which identifies potential reversals.',
            'parameters': [
                {
                    'id': 'volume_threshold',
                    'name': 'Volume Threshold',
                    'description': 'Minimum volume as percentage of 20-day average',
                    'type': 'number',
                    'default': 120,
                    'min': 100,
                    'max': 200
                },
                {
                    'id': 'use_stoch_rsi',
                    'name': 'Use Stochastic RSI',
                    'description': 'Use Stochastic RSI crossover as a filter',
                    'type': 'boolean',
                    'default': True
                },
                {
                    'id': 'use_macd',
                    'name': 'Use MACD Divergence',
                    'description': 'Use MACD histogram divergence as a filter',
                    'type': 'boolean',
                    'default': False
                },
                {
                    'id': 'risk_per_trade',
                    'name': 'Risk Per Trade',
                    'description': 'Percentage of portfolio to risk per trade',
                    'type': 'number',
                    'default': 1.0,
                    'min': 0.1,
                    'max': 5.0
                }
            ],
            'performance': {
                'win_rate': 71.3,
                'profit_factor': 3.42,
                'avg_return': 1.45,
                'max_drawdown': -13.2
            },
            'description_long': """
                The Bull Hook pattern is a short-term price pattern characterized by:
                
                1. The open is above the previous day's high
                2. The close is below the previous day's close
                3. The daily range is narrower than the previous day's range
                
                This pattern represents a failed breakout attempt, where prices initially gap up above 
                the previous day's high but then reverse and close below the previous day's close, 
                creating a "hook" shape on the chart.
                
                The strategy has been enhanced with complementary indicators:
                - Stochastic RSI crossover (74.75% win rate)
                - Volume threshold (>120% of 20-day average)
                - MACD histogram divergence (optional)
                
                Risk management includes:
                - Volatility-adjusted position sizing
                - Tiered profit-taking approach
                - Adaptive stop-loss methodology
            """
        }
        return jsonify(strategy)
    else:
        return jsonify({'error': 'Strategy not found'}), 404


@api_bp.route('/strategies/<strategy_id>/parameters', methods=['GET'])
def get_strategy_parameters(strategy_id):
    """
    Get parameters for a specific strategy
    
    Args:
        strategy_id: ID of the strategy
        
    Returns:
        JSON response with strategy parameters
    """
    try:
        # Get the strategy class
        strategy_class = get_strategy_class(strategy_id)
        
        # Get default parameters
        parameters = strategy_class.get_default_parameters()
        
        return jsonify({'parameters': parameters})
    
    except ValueError:
        return jsonify({'error': 'Strategy not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500