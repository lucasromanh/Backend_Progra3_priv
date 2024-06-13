from flask import Blueprint, request, jsonify
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import UsuarioSchema
from ..utils import generate_password_hash

usuarios_bp = Blueprint('usuarios', __name__)

usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)

@usuarios_bp.route('/usuarios', methods=['GET'])
@token_required
def get_usuarios():
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
    result = call_procedure('ObtenerUsuarios', [])
    return jsonify(result), 200

@usuarios_bp.route('/usuarios/<int:id>', methods=['GET'])
@token_required
def get_usuario(id):
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
    result = call_procedure('ObtenerUsuarioPorID', [id])
    if not result:
        return jsonify({'message': 'User not found'}), 404
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
          $ref: '#/definitions/Usuario'
      400:
        description: Invalid input
    """
    data = request.get_json()
    errors = usuario_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    call_procedure('CrearUsuario', [
        data['Nombre'],
        data['Apellido'],
        data['CorreoElectronico'],
        data.get('Telefono', ''),
        data.get('ImagenPerfil', ''),
        generate_password_hash(data['Password'])
    ])
    return jsonify({'message': 'User created successfully'}), 201

@usuarios_bp.route('/usuarios/<int:id>', methods=['PUT'])
@token_required
def update_usuario(id):
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
def delete_usuario(id):
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
    result = call_procedure('ObtenerUsuarioPorID', [id])
    if not result:
        return jsonify({'message': 'User not found'}), 404
    call_procedure('EliminarUsuario', [id])
    return '', 204
