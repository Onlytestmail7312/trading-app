from .bull_hook import BullHookStrategy

def get_strategy_class(strategy_id):
    """
    Get the strategy class for a given strategy ID
    
    Args:
        strategy_id: ID of the strategy
        
    Returns:
        Strategy class
        
    Raises:
        ValueError: If the strategy ID is not found
    """
    strategies = {
        'bull_hook': BullHookStrategy
    }
    
    if strategy_id not in strategies:
        raise ValueError(f"Strategy not found: {strategy_id}")
    
    return strategies[strategy_id]