from flask import Blueprint, request, jsonify, current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, Usuario
import jwt
import datetime
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-tokens')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Usuario.query.filter_by(UsuarioID=data['UsuarioID']).first()
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User Login
    ---
    tags:
      - auth
    parameters:
      - in: body
        name: body
        schema:
          id: Login
          required:
            - CorreoElectronico
            - Password
          properties:
            CorreoElectronico:
              type: string
              description: The user's email.
            Password:
              type: string
              description: The user's password.
    responses:
      200:
        description: Login successful
        schema:
          id: LoginResponse
          properties:
            token:
              type: string
              description: JWT token
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    if not data or not data['CorreoElectronico'] or not data['Password']:
        return jsonify({'message': 'Could not verify'}), 401
    user = Usuario.query.filter_by(CorreoElectronico=data['CorreoElectronico']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 401
    if check_password_hash(user.PasswordHash, data['Password']):
        token = jwt.encode({'UsuarioID': user.UsuarioID, 'exp': datetime.datetime.now() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Password is incorrect'}), 403
