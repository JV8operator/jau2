import datetime
import os
import re

import jwt
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from models.database import create_user, get_user_by_email, verify_password

auth_bp = Blueprint('auth', __name__)
JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret-key-change-in-prod')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
                
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user = get_user_by_email(data['email'])
            if not current_user:
                raise Exception("User not found")
        except Exception as e:
            return jsonify({'error': 'Token is invalid or expired'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
        
    email = data['email'].strip().lower()
    password = data['password']
    
    # Basic validation
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, email):
        return jsonify({'error': 'Invalid email format'}), 400
        
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
    success = create_user(email, password)
    
    if not success:
        return jsonify({'error': 'Email already exists'}), 409
        
    # Auto-login after signup
    token = jwt.encode({
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, JWT_SECRET, algorithm="HS256")
    
    return jsonify({
        'message': 'Signup successful',
        'token': token,
        'email': email
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
        
    email = data['email'].strip().lower()
    password = data['password']
    
    user = get_user_by_email(email)
    
    if not user or not verify_password(user['password_hash'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
        
    token = jwt.encode({
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, JWT_SECRET, algorithm="HS256")
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'email': email
    }), 200
