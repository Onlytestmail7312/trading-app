from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid
from datetime import datetime, timedelta
from . import api_bp
from ..utils.cache import cache

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request body:
    {
        "email": "user@example.com",
        "password": "securepassword",
        "name": "John Doe"
    }
    
    Returns:
        JSON response with registration status
    """
    data = request.json
    
    # Validate required fields
    required_fields = ['email', 'password', 'name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    email = data['email']
    password = data['password']
    name = data['name']
    
    # In a real application, you would check if the user already exists
    # and store the user in the database
    
    # For now, we'll just return a success response
    user_id = str(uuid.uuid4())
    
    return jsonify({
        'message': 'Registration successful',
        'user_id': user_id
    })


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """
    Log in a user
    
    Request body:
    {
        "email": "user@example.com",
        "password": "securepassword"
    }
    
    Returns:
        JSON response with authentication tokens
    """
    data = request.json
    
    # Validate required fields
    required_fields = ['email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    email = data['email']
    password = data['password']
    
    # In a real application, you would verify the credentials against the database
    # For now, we'll just use a placeholder
    
    # For demonstration purposes, accept any login with a valid email format
    if '@' not in email:
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Generate tokens
    user_id = str(uuid.uuid4())  # In a real app, this would be the actual user ID
    
    access_token = generate_token(
        user_id=user_id,
        token_type='access',
        expires_in=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
    )
    
    refresh_token = generate_token(
        user_id=user_id,
        token_type='refresh',
        expires_in=current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
    )
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user_id,
            'email': email,
            'name': 'Demo User'  # In a real app, this would be the actual user name
        }
    })


@api_bp.route('/auth/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh the access token using a refresh token
    
    Request body:
    {
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    
    Returns:
        JSON response with a new access token
    """
    data = request.json
    
    if 'refresh_token' not in data:
        return jsonify({'error': 'Refresh token is required'}), 400
    
    refresh_token = data['refresh_token']
    
    try:
        # Verify the refresh token
        payload = jwt.decode(
            refresh_token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        
        # Check if it's a refresh token
        if payload.get('token_type') != 'refresh':
            return jsonify({'error': 'Invalid token type'}), 401
        
        # Generate a new access token
        user_id = payload.get('sub')
        
        access_token = generate_token(
            user_id=user_id,
            token_type='access',
            expires_in=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        )
        
        return jsonify({
            'access_token': access_token
        })
    
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Refresh token has expired'}), 401
    
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid refresh token'}), 401


@api_bp.route('/auth/logout', methods=['POST'])
def logout():
    """
    Log out a user by invalidating their tokens
    
    Returns:
        JSON response with logout status
    """
    # In a real application, you would add the token to a blacklist
    # or invalidate it in some other way
    
    return jsonify({
        'message': 'Logout successful'
    })


def generate_token(user_id, token_type, expires_in):
    """
    Generate a JWT token
    
    Args:
        user_id: User ID
        token_type: Token type ('access' or 'refresh')
        expires_in: Token expiration time
        
    Returns:
        JWT token
    """
    payload = {
        'sub': user_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + expires_in,
        'token_type': token_type
    }
    
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token