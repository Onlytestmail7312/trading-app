from flask import current_app
import os
import json
from google.cloud import storage
import tempfile

def upload_file_to_gcs(local_path, gcs_path):
    """
    Upload a file to Google Cloud Storage
    
    Args:
        local_path: Local file path
        gcs_path: Path in GCS bucket
        
    Returns:
        Public URL of the uploaded file
    """
    # Check if we're in production
    if os.environ.get('FLASK_ENV') != 'production':
        # In development, just return the local path
        return local_path
    
    # Get the bucket name from config
    bucket_name = current_app.config['STORAGE_BUCKET']
    
    # Initialize GCS client
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Upload the file
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)
    
    # Make the file publicly accessible
    blob.make_public()
    
    # Return the public URL
    return blob.public_url


def get_file_from_gcs(gcs_path):
    """
    Get a file from Google Cloud Storage
    
    Args:
        gcs_path: Path in GCS bucket
        
    Returns:
        File content
    """
    # Check if we're in production
    if os.environ.get('FLASK_ENV') != 'production':
        # In development, read from local file
        local_path = os.path.join('uploads', gcs_path)
        with open(local_path, 'rb') as f:
            return f.read()
    
    # Get the bucket name from config
    bucket_name = current_app.config['STORAGE_BUCKET']
    
    # Initialize GCS client
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Get the file
    blob = bucket.blob(gcs_path)
    
    # Download the file to a temporary file
    with tempfile.NamedTemporaryFile() as temp:
        blob.download_to_filename(temp.name)
        with open(temp.name, 'rb') as f:
            return f.read()


def save_backtest_result(backtest_id, result):
    """
    Save a backtest result
    
    Args:
        backtest_id: ID of the backtest
        result: Backtest result
        
    Returns:
        None
    """
    # Check if we're in production
    if os.environ.get('FLASK_ENV') == 'production':
        # In production, save to GCS
        # Convert result to JSON
        result_json = json.dumps(result)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
            temp.write(result_json)
            temp_path = temp.name
        
        # Upload to GCS
        gcs_path = f'backtests/{backtest_id}.json'
        upload_file_to_gcs(temp_path, gcs_path)
        
        # Clean up
        os.unlink(temp_path)
    else:
        # In development, save to local file
        os.makedirs('uploads/backtests', exist_ok=True)
        local_path = f'uploads/backtests/{backtest_id}.json'
        
        with open(local_path, 'w') as f:
            json.dump(result, f)


def get_backtest_result(backtest_id):
    """
    Get a backtest result
    
    Args:
        backtest_id: ID of the backtest
        
    Returns:
        Backtest result
    """
    # Check if we're in production
    if os.environ.get('FLASK_ENV') == 'production':
        # In production, get from GCS
        gcs_path = f'backtests/{backtest_id}.json'
        content = get_file_from_gcs(gcs_path)
        
        # Parse JSON
        return json.loads(content)
    else:
        # In development, read from local file
        local_path = f'uploads/backtests/{backtest_id}.json'
        
        if not os.path.exists(local_path):
            return None
        
        with open(local_path, 'r') as f:
            return json.load(f)