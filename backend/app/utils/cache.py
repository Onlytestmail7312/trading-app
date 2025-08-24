from flask import current_app
from flask_caching import Cache

# Initialize cache
cache = Cache()

def init_cache(app):
    """
    Initialize the cache with the application
    
    Args:
        app: Flask application
    """
    cache_config = {
        'CACHE_TYPE': app.config['CACHE_TYPE'],
        'CACHE_DEFAULT_TIMEOUT': app.config['CACHE_DEFAULT_TIMEOUT']
    }
    
    # Add Redis configuration if in production
    if app.config['CACHE_TYPE'] == 'redis':
        cache_config['CACHE_REDIS_URL'] = app.config['CACHE_REDIS_URL']
    
    cache.init_app(app, config=cache_config)