import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-development-only'
    
    # Flask settings
    DEBUG = False
    TESTING = False
    
    # Database settings (Google Firestore in production)
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'firestore'
    
    # Google Cloud Storage settings
    STORAGE_BUCKET = os.environ.get('STORAGE_BUCKET') or 'trading-app-storage'
    
    # API settings
    YAHOO_FINANCE_API_KEY = os.environ.get('YAHOO_FINANCE_API_KEY')
    
    # Cache settings
    CACHE_TYPE = 'simple'  # Use SimpleCache for development
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Stock lists
    NIFTY_50_URL = 'https://archives.nseindia.com/content/indices/ind_nifty50list.csv'
    NIFTY_NEXT_50_URL = 'https://archives.nseindia.com/content/indices/ind_niftynext50list.csv'
    NIFTY_100_URL = 'https://archives.nseindia.com/content/indices/ind_nifty100list.csv'
    NIFTY_200_URL = 'https://archives.nseindia.com/content/indices/ind_nifty200list.csv'
    
    # Backtest settings
    DEFAULT_BACKTEST_PERIOD = 365  # days
    MAX_BACKTEST_PERIOD = 1825  # 5 years in days
    
    # Strategy settings
    STRATEGIES = ['bull_hook']
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-dev-only'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    CACHE_TYPE = 'simple'
    DATABASE_URI = 'sqlite:///dev.db'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    DATABASE_URI = 'sqlite:///test.db'


class ProductionConfig(Config):
    """Production configuration"""
    # Production specific settings
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    
    # Use secure cookies in production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    # CSRF protection
    WTF_CSRF_ENABLED = True


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}