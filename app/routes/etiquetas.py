from flask import Blueprint, request, jsonify
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import EtiquetaSchema

etiquetas_bp = Blueprint('etiquetas', __name__)

etiqueta_schema = EtiquetaSchema()
etiquetas_schema = EtiquetaSchema(many=True)

@etiquetas_bp.route('/etiquetas', methods=['GET'])
@token_required
def get_etiquetas():
    """
    Obtener todas las etiquetas disponibles.
    ---
    tags:
      - etiquetas
    responses:
      200:
        description: Devuelve un listado de todas las etiquetas.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Etiqueta'
    """
    etiquetas = call_procedure('ObtenerTodasLasEtiquetas', [])
    return jsonify({'etiquetas': etiquetas_schema.dump(etiquetas)}), 200

@etiquetas_bp.route('/etiquetas/<int:id>', methods=['GET'])
@token_required
def get_etiqueta(id):
    """
    Obtener detalles de una etiqueta específica por su ID.
    ---
    tags:
      - etiquetas
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la etiqueta a obtener.
    responses:
      200:
        description: Devuelve la etiqueta especificada.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Etiqueta'
      404:
        description: La etiqueta especificada no fue encontrada.
    """
    etiqueta = call_procedure('ObtenerEtiquetaPorID', [id])
    if not etiqueta:
        return jsonify({'message': 'Etiqueta no encontrada'}), 404
    return jsonify({'etiqueta': etiqueta_schema.dump(etiqueta)}), 200

@etiquetas_bp.route('/etiquetas', methods=['POST'])
@token_required
def create_etiqueta():
    """
    Crear una nueva etiqueta.
    ---
    tags:
      - etiquetas
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              nombre:
                type: string
                description: Nombre de la nueva etiqueta.
              color:
                type: string
                description: Color de la nueva etiqueta.
    responses:
      201:
        description: Etiqueta creada exitosamente.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Etiqueta'
      400:
        description: Entrada inválida.
    """
    data = request.get_json()
    nombre = data.get('nombre')
    color = data.get('color')
    if not nombre or not color:
        return jsonify({'message': 'Datos insuficientes para crear una etiqueta'}), 400
    etiqueta_id = call_procedure('CrearEtiqueta', [nombre, color])
    return jsonify({'message': 'Etiqueta creada exitosamente', 'id': etiqueta_id}), 201

@etiquetas_bp.route('/etiquetas/<int:id>', methods=['PUT'])
@token_required
def update_etiqueta(id):
    """
    Actualizar una etiqueta existente.
    ---
    tags:
      - etiquetas
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la etiqueta a actualizar.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              nombre:
                type: string
                description: Nuevo nombre para la etiqueta.
              color:
                type: string
                description: Nuevo color para la etiqueta.
    responses:
      200:
        description: Etiqueta actualizada exitosamente.
      400:
        description: Entrada inválida.
      404:
        description: Etiqueta no encontrada.
    """
    data = request.get_json()
    nombre = data.get('nombre')
    color = data.get('color')
    if not nombre or not color:
        return jsonify({'message': 'Datos insuficientes para actualizar la etiqueta'}), 400
    if not call_procedure('VerificarEtiquetaExistente', [id]):
        return jsonify({'message': 'Etiqueta no encontrada'}), 404
    call_procedure('ActualizarEtiqueta', [id, nombre, color])
    return jsonify({'message': 'Etiqueta actualizada exitosamente'}), 200

@etiquetas_bp.route('/etiquetas/<int:id>', methods=['DELETE'])
@token_required
def delete_etiqueta(id):
    """
    Eliminar una etiqueta existente.
    ---
    tags:
      - etiquetas
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la etiqueta a eliminar.
    responses:
      204:
        description: Etiqueta eliminada exitosamente.
      404:
        description: Etiqueta no encontrada.
    """
    if not call_procedure('VerificarEtiquetaExistente', [id]):
        return jsonify({'message': 'Etiqueta no encontrada'}), 404
    call_procedure('EliminarEtiqueta', [id])
    return '', 204
