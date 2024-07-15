from flask import Blueprint, request, jsonify
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import ComentarioSchema
from ..constants import COMMENT_NOT_FOUND

comentarios_bp = Blueprint('comentarios', __name__)

comentario_schema = ComentarioSchema()
comentarios_schema = ComentarioSchema(many=True)

@comentarios_bp.route('/comentarios', methods=['GET'])
@token_required
def get_comentarios():
    """
    Obtener todos los comentarios.
    ---
    tags:
      - comentarios
    responses:
      200:
        description: Devuelve un listado de todos los comentarios.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Comentario'
    """
    result = call_procedure('ObtenerTodosLosComentarios', [])
    return jsonify({'comentarios': comentarios_schema.dump(result)}), 200

@comentarios_bp.route('/comentarios/<int:id>', methods=['GET'])
@token_required
def get_comentario(id):
    """
    Obtener detalles de un comentario específico por su ID.
    ---
    tags:
      - comentarios
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del comentario a obtener.
    responses:
      200:
        description: Devuelve el comentario especificado.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Comentario'
      404:
        description: El comentario especificado no fue encontrado.
    """
    result = call_procedure('ObtenerComentarioPorID', [id])
    if not result:
        return jsonify({'message': COMMENT_NOT_FOUND}), 404
    return jsonify({'comentario': comentario_schema.dump(result[0])}), 200

@comentarios_bp.route('/comentarios', methods=['POST'])
@token_required
def create_comentario():
    """
    Crear un nuevo comentario.
    ---
    tags:
      - comentarios
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              TareaID:
                type: integer
                description: ID de la tarea asociada al comentario.
              Texto:
                type: string
                description: Texto del comentario.
    responses:
      201:
        description: Comentario creado exitosamente.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Comentario'
      400:
        description: Entrada inválida.
    """
    data = request.get_json()
    errors = comentario_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    comentario_id = call_procedure('CrearComentario', [
        data['TareaID'],
        id.UsuarioID,
        data['Texto']
    ])
    return jsonify({'message': 'Comentario creado exitosamente', 'id': comentario_id}), 201

@comentarios_bp.route('/comentarios/<int:id>', methods=['PUT'])
@token_required
def update_comentario(id):
    """
    Actualizar un comentario existente.
    ---
    tags:
      - comentarios
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del comentario a actualizar.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              Texto:
                type: string
                description: Nuevo texto para el comentario.
    responses:
      200:
        description: Comentario actualizado exitosamente.
      400:
        description: Entrada inválida.
      404:
        description: Comentario no encontrado.
    """
    data = request.get_json()
    errors = comentario_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    result = call_procedure('ObtenerComentarioPorID', [id])
    if not result:
        return jsonify({'message': COMMENT_NOT_FOUND}), 404
    call_procedure('ActualizarComentario', [
        id,
        data['Texto']
    ])
    return jsonify({'message': 'Comentario actualizado exitosamente'}), 200

@comentarios_bp.route('/comentarios/<int:id>', methods=['DELETE'])
@token_required
def delete_comentario(id):
    """
    Eliminar un comentario existente.
    ---
    tags:
      - comentarios
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del comentario a eliminar.
    responses:
      204:
        description: Comentario eliminado exitosamente.
      404:
        description: Comentario no encontrado.
    """
    result = call_procedure('ObtenerComentarioPorID', [id])
    if not result:
        return jsonify({'message': COMMENT_NOT_FOUND}), 404
    call_procedure('EliminarComentario', [id])
    return '', 204
