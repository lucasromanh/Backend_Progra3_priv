from flask import Blueprint, request, jsonify, current_app as app
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from app.models import db, Usuario
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import UsuarioSchema
from ..constants import USER_NOT_FOUND
import jwt
import datetime

usuarios_bp = Blueprint('usuarios', __name__)
CORS(usuarios_bp)  

usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)

@usuarios_bp.route('/usuarios', methods=['GET'])
@token_required
def get_usuarios(current_user):
    """
    Get All Users
    ---
    tags:
      - usuarios
    responses:
      200:
        description: List of users
        schema:
          type: array
          items:
            $ref: '#/definitions/Usuario'
    """
    app.logger.info(f"User accessing all users: {current_user.UsuarioID}")
    result = call_procedure('ObtenerUsuarios', [])
    return jsonify(result), 200

@usuarios_bp.route('/usuarios/<int:id>', methods=['GET'])
@token_required
def get_usuario(current_user, id):
    """
    Get a User by ID
    ---
    tags:
      - usuarios
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the user
    responses:
      200:
        description: User found
        schema:
          $ref: '#/definitions/Usuario'
      404:
        description: User not found
    """
    app.logger.info(f"User accessing user {id}: {current_user.UsuarioID}")
    result = call_procedure('ObtenerUsuarioPorID', [id])
    if not result:
        return jsonify({'message': USER_NOT_FOUND}), 404
    return jsonify(result[0]), 200

@usuarios_bp.route('/usuarios', methods=['POST'])
def create_usuario():
    """
    Create a New User
    ---
    tags:
      - usuarios
    parameters:
      - in: body
        name: body
        schema:
          id: CreateUsuario
          required:
            - Nombre
            - Apellido
            - CorreoElectronico
            - Password
          properties:
            Nombre:
              type: string
            Apellido:
              type: string
            CorreoElectronico:
              type: string
            Password:
              type: string
    responses:
      201:
        description: User created successfully
        schema:
          properties:
            message:
              type: string
            token:
              type: string
      400:
        description: Invalid input
    """
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    required_fields = ['Nombre', 'Apellido', 'CorreoElectronico', 'Password']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'{field} is required'}), 400

    errors = usuario_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    new_user = Usuario(
        Nombre=data['Nombre'],
        Apellido=data['Apellido'],
        CorreoElectronico=data['CorreoElectronico'],
        PasswordHash=generate_password_hash(data['Password'])
    )

    db.session.add(new_user)
    db.session.commit()

    token = jwt.encode({'UsuarioID': new_user.UsuarioID, 'exp': datetime.datetime.now() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({'message': 'User created successfully', 'token': token}), 201

@usuarios_bp.route('/usuarios/<int:id>', methods=['PUT'])
@token_required
def update_usuario(current_user, id):
    """
    Update a User
    ---
    tags:
      - usuarios
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the user
      - in: body
        name: body
        schema:
          id: UpdateUsuario
          properties:
            Nombre:
              type: string
            Apellido:
              type: string
            CorreoElectronico:
              type: string
            Password:
              type: string
    responses:
      200:
        description: User updated successfully
        schema:
          $ref: '#/definitions/Usuario'
      400:
        description: Invalid input
      404:
        description: User not found
    """
    app.logger.info(f"User updating user {id}: {current_user.UsuarioID}")
    data = request.get_json()
    errors = usuario_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    result = call_procedure('ObtenerUsuarioPorID', [id])
    if not result:
        return jsonify({'message': 'User not found'}), 404
    call_procedure('ActualizarUsuario', [
        id,
        data['Nombre'],
        data['Apellido'],
        data['CorreoElectronico'],
        data.get('Telefono', ''),
        data.get('ImagenPerfil', ''),
        generate_password_hash(data['Password'])
    ])
    return jsonify({'message': 'User updated successfully'}), 200

@usuarios_bp.route('/usuarios/<int:id>', methods=['DELETE'])
@token_required
def delete_usuario(current_user, id):
    """
    Delete a User
    ---
    tags:
      - usuarios
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the user
    responses:
      204:
        description: User deleted successfully
      404:
        description: User not found
    """
    app.logger.info(f"User deleting user {id}: {current_user.UsuarioID}")
    result = call_procedure('ObtenerUsuarioPorID', [id])
    if not result:
        return jsonify({'message': 'User not found'}), 404
    call_procedure('EliminarUsuario', [id])
    return '', 204
