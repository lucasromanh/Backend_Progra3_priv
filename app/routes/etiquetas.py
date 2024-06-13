from flask import Blueprint, request, jsonify
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import EtiquetaSchema, TareaEtiquetaSchema
from ..constants import TAG_NOT_FOUND

etiquetas_bp = Blueprint('etiquetas', __name__)

etiqueta_schema = EtiquetaSchema()
etiquetas_schema = EtiquetaSchema(many=True)
tarea_etiqueta_schema = TareaEtiquetaSchema()

@etiquetas_bp.route('/etiquetas', methods=['GET'])
@token_required
def get_etiquetas():
    """
    Get All Tags
    ---
    tags:
      - etiquetas
    responses:
      200:
        description: List of tags
        schema:
          type: array
          items:
            $ref: '#/definitions/Etiqueta'
    """
    result = call_procedure('ObtenerEtiquetas', [])
    return jsonify(result), 200

@etiquetas_bp.route('/etiquetas/<int:id>', methods=['GET'])
@token_required
def get_etiqueta(id):
    """
    Get a Tag by ID
    ---
    tags:
      - etiquetas
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the tag
    responses:
      200:
        description: Tag found
        schema:
          $ref: '#/definitions/Etiqueta'
      404:
        description: Tag not found
    """
    result = call_procedure('ObtenerEtiquetaPorID', [id])
    if not result:
        return jsonify({'message': TAG_NOT_FOUND}), 404
    return jsonify(result[0]), 200

@etiquetas_bp.route('/etiquetas', methods=['POST'])
@token_required
def create_etiqueta():
    """
    Create a New Tag
    ---
    tags:
      - etiquetas
    parameters:
      - in: body
        name: body
        schema:
          id: CreateEtiqueta
          required:
            - Nombre
          properties:
            Nombre:
              type: string
    responses:
      201:
        description: Tag created successfully
        schema:
          $ref: '#/definitions/Etiqueta'
      400:
        description: Invalid input
    """
    data = request.get_json()
    errors = etiqueta_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    call_procedure('CrearEtiqueta', [
        data['Nombre']
    ])
    return jsonify({'message': 'Tag created successfully'}), 201

@etiquetas_bp.route('/etiquetas/<int:id>', methods=['PUT'])
@token_required
def update_etiqueta(id):
    """
    Update a Tag
    ---
    tags:
      - etiquetas
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the tag
      - in: body
        name: body
        schema:
          id: UpdateEtiqueta
          properties:
            Nombre:
              type: string
    responses:
      200:
        description: Tag updated successfully
        schema:
          $ref: '#/definitions/Etiqueta'
      400:
        description: Invalid input
      404:
        description: Tag not found
    """
    data = request.get_json()
    errors = etiqueta_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    result = call_procedure('ObtenerEtiquetaPorID', [id])
    if not result:
        return jsonify({'message': 'Tag not found'}), 404
    call_procedure('ActualizarEtiqueta', [
        id,
        data['Nombre']
    ])
    return jsonify({'message': 'Tag updated successfully'}), 200

@etiquetas_bp.route('/etiquetas/<int:id>', methods=['DELETE'])
@token_required
def delete_etiqueta(id):
    """
    Delete a Tag
    ---
    tags:
      - etiquetas
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the tag
    responses:
      204:
        description: Tag deleted successfully
      404:
        description: Tag not found
    """
    result = call_procedure('ObtenerEtiquetaPorID', [id])
    if not result:
        return jsonify({'message': 'Tag not found'}), 404
    call_procedure('EliminarEtiqueta', [id])
    return '', 204

@etiquetas_bp.route('/tareas/<int:tarea_id>/etiquetas', methods=['POST'])
@token_required
def add_etiqueta_to_tarea(tarea_id):
    """
    Add Tag to Task
    ---
    tags:
      - etiquetas
    parameters:
      - in: body
        name: body
        schema:
          id: AddEtiquetaToTarea
          required:
            - EtiquetaID
          properties:
            EtiquetaID:
              type: integer
    responses:
      201:
        description: Tag added to task successfully
        schema:
          $ref: '#/definitions/TareaEtiqueta'
      400:
        description: Invalid input
    """
    data = request.get_json()
    errors = tarea_etiqueta_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    call_procedure('AgregarEtiquetaATarea', [
        tarea_id,
        data['EtiquetaID']
    ])
    return jsonify({'message': 'Tag added to task successfully'}), 201

@etiquetas_bp.route('/tareas/<int:tarea_id>/etiquetas/<int:etiqueta_id>', methods=['DELETE'])
@token_required
def remove_etiqueta_from_tarea(tarea_id, etiqueta_id):
    """
    Remove Tag from Task
    ---
    tags:
      - etiquetas
    parameters:
      - in: path
        name: tarea_id
        type: integer
        required: true
        description: ID of the task
      - in: path
        name: etiqueta_id
        type: integer
        required: true
        description: ID of the tag
    responses:
      204:
        description: Tag removed from task successfully
      404:
        description: Tag or Task not found
    """
    call_procedure('RemoverEtiquetaDeTarea', [
        tarea_id,
        etiqueta_id
    ])
    return '', 204
