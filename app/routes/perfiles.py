from flask import Blueprint, request, jsonify
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import PerfilUsuarioSchema
from ..constants import PROFILE_NOT_FOUND

perfiles_bp = Blueprint('perfiles', __name__)

perfil_schema = PerfilUsuarioSchema()
perfiles_schema = PerfilUsuarioSchema(many=True)

@perfiles_bp.route('/perfiles', methods=['GET'])
@token_required
def get_perfiles():
    """
    Get All Profiles
    ---
    tags:
      - perfiles
    responses:
      200:
        description: List of profiles
        schema:
          type: array
          items:
            $ref: '#/definitions/PerfilUsuario'
    """
    result = call_procedure('ObtenerPerfilesUsuario', [])
    return jsonify(result), 200

@perfiles_bp.route('/perfiles/<int:id>', methods=['GET'])
@token_required
def get_perfil(id):
    """
    Get a Profile by ID
    ---
    tags:
      - perfiles
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the profile
    responses:
      200:
        description: Profile found
        schema:
          $ref: '#/definitions/PerfilUsuario'
      404:
        description: Profile not found
    """
    result = call_procedure('ObtenerPerfilUsuarioPorID', [id])
    if not result:
        return jsonify({'message': PROFILE_NOT_FOUND}), 404
    return jsonify(result[0]), 200

@perfiles_bp.route('/perfiles', methods=['POST'])
@token_required
def create_perfil():
    """
    Create a New Profile
    ---
    tags:
      - perfiles
    parameters:
      - in: body
        name: body
        schema:
          id: CreatePerfil
          required:
            - UsuarioID
          properties:
            UsuarioID:
              type: integer
            Editable:
              type: boolean
            Biografia:
              type: string
            Intereses:
              type: string
            Ocupacion:
              type: string
    responses:
      201:
        description: Profile created successfully
        schema:
          $ref: '#/definitions/PerfilUsuario'
      400:
        description: Invalid input
    """
    data = request.get_json()
    errors = perfil_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    call_procedure('CrearPerfilUsuario', [
        data['UsuarioID'],
        data.get('Editable', True),
        data.get('Biografia', ''),
        data.get('Intereses', ''),
        data.get('Ocupacion', '')
    ])
    return jsonify({'message': 'Profile created successfully'}), 201

@perfiles_bp.route('/perfiles/<int:id>', methods=['PUT'])
@token_required
def update_perfil(id):
    """
    Update a Profile
    ---
    tags:
      - perfiles
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the profile
      - in: body
        name: body
        schema:
          id: UpdatePerfil
          properties:
            Editable:
              type: boolean
            Biografia:
              type: string
            Intereses:
              type: string
            Ocupacion:
              type: string
    responses:
      200:
        description: Profile updated successfully
        schema:
          $ref: '#/definitions/PerfilUsuario'
      400:
        description: Invalid input
      404:
        description: Profile not found
    """
    data = request.get_json()
    errors = perfil_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    result = call_procedure('ObtenerPerfilUsuarioPorID', [id])
    if not result:
        return jsonify({'message': 'Profile not found'}), 404
    call_procedure('ActualizarPerfilUsuario', [
        id,
        data['UsuarioID'],
        data.get('Editable', True),
        data.get('Biografia', ''),
        data.get('Intereses', ''),
        data.get('Ocupacion', '')
    ])
    return jsonify({'message': 'Profile updated successfully'}), 200

@perfiles_bp.route('/perfiles/<int:id>', methods=['DELETE'])
@token_required
def delete_perfil(id):
    """
    Delete a Profile
    ---
    tags:
      - perfiles
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the profile
    responses:
      204:
        description: Profile deleted successfully
      404:
        description: Profile not found
    """
    result = call_procedure('ObtenerPerfilUsuarioPorID', [id])
    if not result:
        return jsonify({'message': 'Profile not found'}), 404
    call_procedure('EliminarPerfilUsuario', [id])
    return '', 204
