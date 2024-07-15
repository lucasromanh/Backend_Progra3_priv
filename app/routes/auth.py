from flask import Blueprint, request, jsonify, current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, Usuario, Board
import jwt
import datetime
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            token = token.split(" ")[1]  # Extraer el token de 'Bearer <token>'
            app.logger.info(f"Token received: {token}")
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Usuario.query.filter_by(UsuarioID=data['UsuarioID']).first()
            app.logger.info(f"Token decoded successfully: {data}")
        except jwt.ExpiredSignatureError:
            app.logger.error("Token expired")
            return jsonify({'message': 'Token expired'}), 403
        except jwt.InvalidTokenError as e:
            app.logger.error(f"Invalid token: {e}")
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 403
        except Exception as e:
            app.logger.error(f"Token decoding error: {e}")
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
    if not data or not data.get('CorreoElectronico') or not data.get('Password'):
        return jsonify({'message': 'Could not verify'}), 401

    user = Usuario.query.filter_by(CorreoElectronico=data['CorreoElectronico']).first()

    if not user:
        return jsonify({'message': 'User not found'}), 401

    if check_password_hash(user.PasswordHash, data['Password']):
        token = jwt.encode({'UsuarioID': user.UsuarioID, 'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
        user_data = {
            'UsuarioID': user.UsuarioID,
            'defaultBoardId': user.defaultBoardId
        }
        app.logger.info(f"User data to be sent: {user_data}")
        return jsonify({'token': token, 'user': user_data})

    return jsonify({'message': 'Password is incorrect'}), 403

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    User Registration
    ---
    tags:
      - auth
    parameters:
      - in: body
        name: body
        schema:
          id: Register
          required:
            - CorreoElectronico
            - Password
            - Nombre
            - Apellido
          properties:
            CorreoElectronico:
              type: string
              description: The user's email.
            Password:
              type: string
              description: The user's password.
            Nombre:
              type: string
              description: The user's first name.
            Apellido:
              type: string
              description: The user's last name.
    responses:
      201:
        description: User registered successfully
      400:
        description: Invalid input
    """
    data = request.get_json()
    hashed_password = generate_password_hash(data['Password'], method='pbkdf2:sha256')
    new_user = Usuario(
        Nombre=data['Nombre'],
        Apellido=data['Apellido'],
        CorreoElectronico=data['CorreoElectronico'],
        PasswordHash=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    
    default_board = Board(
        UsuarioPropietarioID=new_user.UsuarioID,
        Titulo="Tablero Predeterminado"
    )
    db.session.add(default_board)
    db.session.commit()

    new_user.defaultBoardId = default_board.BoardID
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """
    User Logout
    ---
    tags:
      - auth
    responses:
      200:
        description: Logout successful
    """
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/refresh-token', methods=['POST'])
@token_required
def refresh_token(current_user):
    """
    Refresh Token
    ---
    tags:
      - auth
    responses:
      200:
        description: Token refreshed successfully
        schema:
          id: RefreshTokenResponse
          properties:
            token:
              type: string
              description: New JWT token
      403:
        description: Token is missing or invalid
    """
    token = jwt.encode({'UsuarioID': current_user.UsuarioID, 'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'token': token})
