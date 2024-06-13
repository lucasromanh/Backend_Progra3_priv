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
    Get All Comments
    ---
    tags:
      - comentarios
    responses:
      200:
        description: List of comments
        schema:
          type: array
          items:
            $ref: '#/definitions/Comentario'
    """
    result = call_procedure('ObtenerComentarios', [])
    return jsonify(result), 200

@comentarios_bp.route('/comentarios/<int:id>', methods=['GET'])
@token_required
def get_comentario(id):
    """
    Get a Comment by ID
    ---
    tags:
      - comentarios
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the comment
    responses:
      200:
        description: Comment found
        schema:
          $ref: '#/definitions/Comentario'
      404:
        description: Comment not found
    """
    result = call_procedure('ObtenerComentarioPorID', [id])
    if not result:
        return jsonify({'message': COMMENT_NOT_FOUND}), 404
    return jsonify(result[0]), 200

@comentarios_bp.route('/comentarios', methods=['POST'])
@token_required
def create_comentario():
    """
    Create a New Comment
    ---
    tags:
      - comentarios
    parameters:
      - in: body
        name: body
        schema:
          id: CreateComentario
          required:
            - TareaID
            - Texto
          properties:
            TareaID:
              type: integer
            Texto:
              type: string
    responses:
      201:
        description: Comment created successfully
        schema:
          $ref: '#/definitions/Comentario'
      400:
        description: Invalid input
    """
    data = request.get_json()
    errors = comentario_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    call_procedure('CrearComentario', [
        data['TareaID'],
        id.UsuarioID,
        data['Texto']
    ])
    return jsonify({'message': 'Comment created successfully'}), 201

@comentarios_bp.route('/comentarios/<int:id>', methods=['PUT'])
@token_required
def update_comentario(id):
    """
    Update a Comment
    ---
    tags:
      - comentarios
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the comment
      - in: body
        name: body
        schema:
          id: UpdateComentario
          properties:
            Texto:
              type: string
    responses:
      200:
        description: Comment updated successfully
        schema:
          $ref: '#/definitions/Comentario'
      400:
        description: Invalid input
      404:
        description: Comment not found
    """
    data = request.get_json()
    errors = comentario_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    result = call_procedure('ObtenerComentarioPorID', [id])
    if not result:
        return jsonify({'message': 'Comment not found'}), 404
    call_procedure('ActualizarComentario', [
        id,
        data['Texto']
    ])
    return jsonify({'message': 'Comment updated successfully'}), 200

@comentarios_bp.route('/comentarios/<int:id>', methods=['DELETE'])
@token_required
def delete_comentario(id):
    """
    Delete a Comment
    ---
    tags:
      - comentarios
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the comment
    responses:
      204:
        description: Comment deleted successfully
      404:
        description: Comment not found
    """
    result = call_procedure('ObtenerComentarioPorID', [id])
    if not result:
        return jsonify({'message': 'Comment not found'}), 404
    call_procedure('EliminarComentario', [id])
    return '', 204
