from flask import Blueprint, request, jsonify
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import NotificacionSchema
from ..constants import NOTIFICATION_NOT_FOUND

notificaciones_bp = Blueprint('notificaciones', __name__)

notificacion_schema = NotificacionSchema()
notificaciones_schema = NotificacionSchema(many=True)

@notificaciones_bp.route('/notificaciones', methods=['GET'])
@token_required
def get_notificaciones():
    """
    Obtener todas las notificaciones.
    ---
    tags:
      - notificaciones
    responses:
      200:
        description: Devuelve un listado de todas las notificaciones.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Notificacion'
    """
    result = call_procedure('ObtenerTodasLasNotificaciones', [])
    return jsonify({'notificaciones': notificaciones_schema.dump(result)}), 200

@notificaciones_bp.route('/notificaciones/<int:id>', methods=['GET'])
@token_required
def get_notificacion(id):
    """
    Obtener detalles de una notificación específica por su ID.
    ---
    tags:
      - notificaciones
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la notificación a obtener.
    responses:
      200:
        description: Devuelve la notificación especificada.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Notificacion'
      404:
        description: La notificación especificada no fue encontrada.
    """
    result = call_procedure('ObtenerNotificacionPorID', [id])
    if not result:
        return jsonify({'message': NOTIFICATION_NOT_FOUND}), 404
    return jsonify({'notificacion': notificacion_schema.dump(result[0])}), 200

@notificaciones_bp.route('/notificaciones', methods=['POST'])
@token_required
def create_notificacion():
    """
    Crear una nueva notificación.
    ---
    tags:
      - notificaciones
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              UsuarioID:
                type: integer
                description: ID del usuario al que se envía la notificación.
              Mensaje:
                type: string
                description: Mensaje de la notificación.
    responses:
      201:
        description: Notificación creada exitosamente.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Notificacion'
      400:
        description: Entrada inválida.
    """
    data = request.get_json()
    errors = notificacion_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    notificacion_id = call_procedure('CrearNotificacion', [
        data['UsuarioID'],
        data['Mensaje'],
        False
    ])
    return jsonify({'message': 'Notificación creada exitosamente', 'id': notificacion_id}), 201

@notificaciones_bp.route('/notificaciones/<int:id>', methods=['PUT'])
@token_required
def update_notificacion(id):
    """
    Actualizar una notificación existente.
    ---
    tags:
      - notificaciones
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la notificación a actualizar.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              Mensaje:
                type: string
                description: Nuevo mensaje para la notificación.
              Leida:
                type: boolean
                description: Estado de lectura de la notificación.
    responses:
      200:
        description: Notificación actualizada exitosamente.
      400:
        description: Entrada inválida.
      404:
        description: Notificación no encontrada.
    """
    data = request.get_json()
    errors = notificacion_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    if not call_procedure('VerificarNotificacionExistente', [id]):
        return jsonify({'message': NOTIFICATION_NOT_FOUND}), 404
    call_procedure('ActualizarNotificacion', [
        id,
        data['Mensaje'],
        data.get('Leida', False)
    ])
    return jsonify({'message': 'Notificación actualizada exitosamente'}), 200

@notificaciones_bp.route('/notificaciones/<int:id>', methods=['DELETE'])
@token_required
def delete_notificacion(id):
    """
    Eliminar una notificación existente.
    ---
    tags:
      - notificaciones
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la notificación a eliminar.
    responses:
      204:
        description: Notificación eliminada exitosamente.
      404:
        description: Notificación no encontrada.
    """
    if not call_procedure('VerificarNotificacionExistente', [id]):
        return jsonify({'message': NOTIFICATION_NOT_FOUND}), 404
    call_procedure('EliminarNotificacion', [id])
    return '', 204
