import os
from app import create_app
from app.config import config_by_name
from app.utils.cache import init_cache

# Get environment
env = os.environ.get('FLASK_ENV', 'development')

# Create app with the appropriate configuration
app = create_app(config_by_name[env])

# Initialize cache
init_cache(app)

if __name__ == '__main__':
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)