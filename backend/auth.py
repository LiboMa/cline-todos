from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity
from datetime import timedelta
from backend.models import db, User

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

def init_jwt(app):
    jwt = JWTManager(app)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid token',
            'message': 'The token is invalid or expired'
        }), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({
            'error': 'No token provided',
            'message': 'Authentication token is missing'
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({
            'error': 'Token expired',
            'message': 'The token has expired'
        }), 401

    return jwt

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    try:
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(days=1)
        )
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create user', 'message': str(e)}), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(field in data for field in ['username', 'password']):
            return jsonify({'error': 'Missing username or password'}), 400
        
        # Find user and verify password
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401
            
        if not user.check_password(data['password']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Create access token
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(days=1)
        )
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token
        })
    except Exception as e:
        return jsonify({'error': 'Login failed', 'message': str(e)}), 500
