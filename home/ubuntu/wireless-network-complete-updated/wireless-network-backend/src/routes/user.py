from flask import Blueprint

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users - endpoint اختياري"""
    return {'users': [], 'message': 'User management endpoint'}

@user_bp.route('/users', methods=['POST'])
def create_user():
    """Create new user - endpoint اختياري"""
    return {'message': 'User created successfully'}

