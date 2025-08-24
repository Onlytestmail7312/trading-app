from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
import pandas as pd
import requests
import os
import uuid
from . import api_bp
from ..utils.storage import upload_file_to_gcs, get_file_from_gcs
from ..utils.cache import cache

@api_bp.route('/stock-lists', methods=['GET'])
def get_stock_lists():
    """
    Get available stock lists
    
    Returns:
        JSON response with available stock lists
    """
    stock_lists = [
        {'id': 'nifty_50', 'name': 'Nifty 50', 'description': 'Top 50 companies by market capitalization'},
        {'id': 'nifty_next_50', 'name': 'Nifty Next 50', 'description': 'Next 50 companies after Nifty 50'},
        {'id': 'nifty_100', 'name': 'Nifty 100', 'description': 'Top 100 companies by market capitalization'},
        {'id': 'nifty_200', 'name': 'Nifty 200', 'description': 'Top 200 companies by market capitalization'},
        {'id': 'custom', 'name': 'Custom List', 'description': 'Upload your own list of stocks'}
    ]
    
    # Get user's custom lists if authenticated
    # This would be expanded in a real application with user authentication
    
    return jsonify({'stock_lists': stock_lists})


@api_bp.route('/stock-lists/<list_id>', methods=['GET'])
@cache.cached(timeout=86400)  # Cache for 24 hours
def get_stock_list(list_id):
    """
    Get stocks for a specific list
    
    Args:
        list_id: ID of the stock list
        
    Returns:
        JSON response with stocks in the list
    """
    if list_id == 'nifty_50':
        url = current_app.config['NIFTY_50_URL']
        stocks = _fetch_nse_stocks(url)
    elif list_id == 'nifty_next_50':
        url = current_app.config['NIFTY_NEXT_50_URL']
        stocks = _fetch_nse_stocks(url)
    elif list_id == 'nifty_100':
        url = current_app.config['NIFTY_100_URL']
        stocks = _fetch_nse_stocks(url)
    elif list_id == 'nifty_200':
        url = current_app.config['NIFTY_200_URL']
        stocks = _fetch_nse_stocks(url)
    elif list_id.startswith('custom_'):
        # Get custom list from storage
        custom_id = list_id.replace('custom_', '')
        stocks = _get_custom_stock_list(custom_id)
    else:
        return jsonify({'error': 'Invalid stock list ID'}), 400
    
    return jsonify({'stocks': stocks})


@api_bp.route('/stock-lists/custom', methods=['POST'])
def upload_custom_list():
    """
    Upload a custom stock list
    
    Returns:
        JSON response with the ID of the uploaded list
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are supported'}), 400
    
    # Generate a unique ID for the custom list
    custom_id = str(uuid.uuid4())
    
    # Save the file temporarily
    filename = secure_filename(file.filename)
    temp_path = os.path.join('/tmp', filename)
    file.save(temp_path)
    
    try:
        # Validate the CSV format
        df = pd.read_csv(temp_path)
        
        # Check if the CSV has the required columns
        required_columns = ['Symbol']
        if not all(col in df.columns for col in required_columns):
            return jsonify({'error': 'CSV must contain a Symbol column'}), 400
        
        # Upload to Google Cloud Storage in production
        # For development, we'll just save it locally
        if os.environ.get('FLASK_ENV') == 'production':
            file_path = f'custom_lists/{custom_id}.csv'
            upload_file_to_gcs(temp_path, file_path)
        else:
            os.makedirs('uploads/custom_lists', exist_ok=True)
            file_path = f'uploads/custom_lists/{custom_id}.csv'
            os.rename(temp_path, file_path)
        
        # Extract stock symbols
        stocks = df['Symbol'].tolist()
        
        # In a real application, we would associate this list with the user
        # and store the metadata in the database
        
        return jsonify({
            'id': f'custom_{custom_id}',
            'name': os.path.splitext(filename)[0],
            'stocks': stocks
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)


def _fetch_nse_stocks(url):
    """
    Fetch stocks from NSE CSV URL
    
    Args:
        url: URL of the NSE CSV file
        
    Returns:
        List of stock symbols
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Save the CSV content to a temporary file
        temp_file = '/tmp/nse_stocks.csv'
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        # Read the CSV file
        df = pd.read_csv(temp_file)
        
        # Extract the stock symbols and add .NS suffix for Yahoo Finance
        if 'Symbol' in df.columns:
            stocks = [f"{symbol}.NS" for symbol in df['Symbol'].tolist()]
        else:
            stocks = []
        
        # Clean up
        os.remove(temp_file)
        
        return stocks
    
    except Exception as e:
        current_app.logger.error(f"Error fetching NSE stocks: {str(e)}")
        return []


def _get_custom_stock_list(custom_id):
    """
    Get custom stock list from storage
    
    Args:
        custom_id: ID of the custom list
        
    Returns:
        List of stock symbols
    """
    try:
        if os.environ.get('FLASK_ENV') == 'production':
            # Get from Google Cloud Storage
            file_path = f'custom_lists/{custom_id}.csv'
            content = get_file_from_gcs(file_path)
            
            # Save to temporary file
            temp_file = f'/tmp/{custom_id}.csv'
            with open(temp_file, 'wb') as f:
                f.write(content)
            
            # Read the CSV
            df = pd.read_csv(temp_file)
            
            # Clean up
            os.remove(temp_file)
        else:
            # Read from local file
            file_path = f'uploads/custom_lists/{custom_id}.csv'
            df = pd.read_csv(file_path)
        
        # Extract stock symbols
        stocks = df['Symbol'].tolist()
        
        return stocks
    
    except Exception as e:
        current_app.logger.error(f"Error getting custom stock list: {str(e)}")
        return []