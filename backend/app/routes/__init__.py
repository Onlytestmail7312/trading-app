from flask import Blueprint

# Create a Blueprint for API routes
api_bp = Blueprint('api', __name__)

# Import routes after creating the Blueprint to avoid circular imports
from .stock_lists import *
from .strategies import *
from .backtest import *
from .monitoring import *
from .auth import *