from flask import Flask
from flask_cors import CORS
from .config import Config
from .routes import api_bp
import os

def create_app(config_class=Config):
    """
    Create and configure the Flask application
    
    Args:
        config_class: Configuration class
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create a simple route for health check
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}
    
    return app