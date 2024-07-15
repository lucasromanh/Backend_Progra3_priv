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
    Obtener todos los perfiles.
    ---
    tags:
      - perfiles
    responses:
      200:
        description: Devuelve un listado de todos los perfiles.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/PerfilUsuario'
    """
    result = call_procedure('ObtenerPerfilesUsuario', [])
    return jsonify({'perfiles': perfiles_schema.dump(result)}), 200

@perfiles_bp.route('/perfiles/<int:id>', methods=['GET'])
@token_required
def get_perfil(id):
    """
    Obtener detalles de un perfil específico por su ID.
    ---
    tags:
      - perfiles
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del perfil a obtener.
    responses:
      200:
        description: Devuelve el perfil especificado.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PerfilUsuario'
      404:
        description: El perfil especificado no fue encontrado.
    """
    result = call_procedure('ObtenerPerfilUsuarioPorID', [id])
    if not result:
        return jsonify({'message': PROFILE_NOT_FOUND}), 404
    return jsonify({'perfil': perfil_schema.dump(result[0])}), 200

@perfiles_bp.route('/perfiles', methods=['POST'])
@token_required
def create_perfil():
    """
    Crear un nuevo perfil.
    ---
    tags:
      - perfiles
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              UsuarioID:
                type: integer
                description: ID del usuario asociado al perfil.
              Editable:
                type: boolean
                description: Indica si el perfil es editable.
              Biografia:
                type: string
                description: Biografía del usuario.
              Intereses:
                type: string
                description: Intereses del usuario.
              Ocupacion:
                type: string
                description: Ocupación del usuario.
    responses:
      201:
        description: Perfil creado exitosamente.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PerfilUsuario'
      400:
        description: Entrada inválida.
    """
    data = request.get_json()
    errors = perfil_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    perfil_id = call_procedure('CrearPerfilUsuario', [
        data['UsuarioID'],
        data.get('Editable', True),
        data.get('Biografia', ''),
        data.get('Intereses', ''),
        data.get('Ocupacion', '')
    ])
    return jsonify({'message': 'Perfil creado exitosamente', 'id': perfil_id}), 201

@perfiles_bp.route('/perfiles/<int:id>', methods=['PUT'])
@token_required
def update_perfil(id):
    """
    Actualizar un perfil existente.
    ---
    tags:
      - perfiles
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del perfil a actualizar.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              UsuarioID:
                type: integer
                description: ID del usuario asociado al perfil.
              Editable:
                type: boolean
                description: Indica si el perfil es editable.
              Biografia:
                type: string
                description: Biografía del usuario.
              Intereses:
                type: string
                description: Intereses del usuario.
              Ocupacion:
                type: string
                description: Ocupación del usuario.
    responses:
      200:
        description: Perfil actualizado exitosamente.
      400:
        description: Entrada inválida.
      404:
        description: Perfil no encontrado.
    """
    data = request.get_json()
    errors = perfil_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    if not call_procedure('VerificarPerfilUsuarioExistente', [id]):
        return jsonify({'message': PROFILE_NOT_FOUND}), 404
    call_procedure('ActualizarPerfilUsuario', [
        id,
        data['UsuarioID'],
        data.get('Editable', True),
        data.get('Biografia', ''),
        data.get('Intereses', ''),
        data.get('Ocupacion', '')
    ])
    return jsonify({'message': 'Perfil actualizado exitosamente'}), 200

@perfiles_bp.route('/perfiles/<int:id>', methods=['DELETE'])
@token_required
def delete_perfil(id):
    """
    Eliminar un perfil existente.
    ---
    tags:
      - perfiles
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del perfil a eliminar.
    responses:
      204:
        description: Perfil eliminado exitosamente.
      404:
        description: Perfil no encontrado.
    """
    if not call_procedure('VerificarPerfilUsuarioExistente', [id]):
        return jsonify({'message': PROFILE_NOT_FOUND}), 404
    call_procedure('EliminarPerfilUsuario', [id])
    return '', 204
