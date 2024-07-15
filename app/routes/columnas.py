from flask import Blueprint, request, jsonify
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import ColumnaSchema

columnas_bp = Blueprint('columnas', __name__)

columna_schema = ColumnaSchema()
columnas_schema = ColumnaSchema(many=True)

@columnas_bp.route('/columnas', methods=['GET'])
@token_required
def get_columnas(current_user):
    """
    Obtener todas las columnas.
    ---
    tags:
      - columnas
    responses:
      200:
        description: Devuelve un listado de todas las columnas.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Columna'
    """
    columnas = call_procedure('ObtenerTodasLasColumnas', [])
    return jsonify({'columnas': columnas_schema.dump(columnas)}), 200

@columnas_bp.route('/columnas/<int:id>', methods=['GET'])
@token_required
def get_columna(id):
    """
    Obtener detalles de una columna específica por su ID.
    ---
    tags:
      - columnas
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la columna a obtener.
    responses:
      200:
        description: Devuelve la columna especificada.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Columna'
      404:
        description: La columna especificada no fue encontrada.
    """
    columna = call_procedure('ObtenerColumnaPorID', [id])
    if not columna:
        return jsonify({'message': 'Columna no encontrada'}), 404
    return jsonify({'columna': columna_schema.dump(columna)}), 200

@columnas_bp.route('/columnas', methods=['POST'])
@token_required
def create_columna(current_user):
    """
    Crear una nueva columna.
    ---
    tags:
      - columnas
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              ProyectoID:
                type: integer
                description: ID del proyecto al que pertenece la columna.
              ColumnaNombre:
                type: string
                description: Nombre de la nueva columna.
    responses:
      201:
        description: Columna creada exitosamente.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Columna'
      400:
        description: Entrada inválida.
    """
    data = request.get_json()
    proyecto_id = data.get('ProyectoID')
    columna_nombre = data.get('ColumnaNombre')
    if not proyecto_id or not columna_nombre:
        return jsonify({'message': 'Datos insuficientes para crear una columna'}), 400
    columna_id = call_procedure('CrearColumna', [proyecto_id, columna_nombre])
    return jsonify({'message': 'Columna creada exitosamente', 'id': columna_id}), 201

@columnas_bp.route('/columnas/<int:id>', methods=['PUT'])
@token_required
def update_columna(id):
    """
    Actualizar una columna existente.
    ---
    tags:
      - columnas
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la columna a actualizar.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              ColumnaNombre:
                type: string
                description: Nuevo nombre para la columna.
    responses:
      200:
        description: Columna actualizada exitosamente.
      400:
        description: Entrada inválida.
      404:
        description: Columna no encontrada.
    """
    data = request.get_json()
    columna_nombre = data.get('ColumnaNombre')
    if not columna_nombre:
        return jsonify({'message': 'Datos insuficientes para actualizar la columna'}), 400
    if not call_procedure('VerificarColumnaExistente', [id]):
        return jsonify({'message': 'Columna no encontrada'}), 404
    call_procedure('ActualizarColumna', [id, columna_nombre])
    return jsonify({'message': 'Columna actualizada exitosamente'}), 200

@columnas_bp.route('/columnas/<int:id>', methods=['DELETE'])
@token_required
def delete_columna(id):
    """
    Eliminar una columna existente.
    ---
    tags:
      - columnas
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la columna a eliminar.
    responses:
      204:
        description: Columna eliminada exitosamente.
      404:
        description: Columna no encontrada.
    """
    if not call_procedure('VerificarColumnaExistente', [id]):
        return jsonify({'message': 'Columna no encontrada'}), 404
    call_procedure('EliminarColumna', [id])
    return '', 204
