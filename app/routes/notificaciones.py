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
    Get All Notifications
    ---
    tags:
      - notificaciones
    responses:
      200:
        description: List of notifications
        schema:
          type: array
          items:
            $ref: '#/definitions/Notificacion'
    """
    result = call_procedure('ObtenerNotificaciones', [])
    return jsonify(result), 200

@notificaciones_bp.route('/notificaciones/<int:id>', methods=['GET'])
@token_required
def get_notificacion(id):
    """
    Get a Notification by ID
    ---
    tags:
      - notificaciones
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the notification
    responses:
      200:
        description: Notification found
        schema:
          $ref: '#/definitions/Notificacion'
      404:
        description: Notification not found
    """
    result = call_procedure('ObtenerNotificacionPorID', [id])
    if not result:
        return jsonify({'message': NOTIFICATION_NOT_FOUND}), 404
    return jsonify(result[0]), 200

@notificaciones_bp.route('/notificaciones', methods=['POST'])
@token_required
def create_notificacion():
    """
    Create a New Notification
    ---
    tags:
      - notificaciones
    parameters:
      - in: body
        name: body
        schema:
          id: CreateNotificacion
          required:
            - UsuarioID
            - Mensaje
          properties:
            UsuarioID:
              type: integer
            Mensaje:
              type: string
    responses:
      201:
        description: Notification created successfully
        schema:
          $ref: '#/definitions/Notificacion'
      400:
        description: Invalid input
    """
    data = request.get_json()
    errors = notificacion_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    call_procedure('CrearNotificacion', [
        data['UsuarioID'],
        data['Mensaje'],
        False
    ])
    return jsonify({'message': 'Notification created successfully'}), 201

@notificaciones_bp.route('/notificaciones/<int:id>', methods=['PUT'])
@token_required
def update_notificacion(id):
    """
    Update a Notification
    ---
    tags:
      - notificaciones
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the notification
      - in: body
        name: body
        schema:
          id: UpdateNotificacion
          properties:
            Mensaje:
              type: string
            Leida:
              type: boolean
    responses:
      200:
        description: Notification updated successfully
        schema:
          $ref: '#/definitions/Notificacion'
      400:
        description: Invalid input
      404:
        description: Notification not found
    """
    data = request.get_json()
    errors = notificacion_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    result = call_procedure('ObtenerNotificacionPorID', [id])
    if not result:
        return jsonify({'message': 'Notification not found'}), 404
    call_procedure('ActualizarNotificacion', [
        id,
        data['Mensaje'],
        data.get('Leida', False)
    ])
    return jsonify({'message': 'Notification updated successfully'}), 200

@notificaciones_bp.route('/notificaciones/<int:id>', methods=['DELETE'])
@token_required
def delete_notificacion(id):
    """
    Delete a Notification
    ---
    tags:
      - notificaciones
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the notification
    responses:
      204:
        description: Notification deleted successfully
      404:
        description: Notification not found
    """
    result = call_procedure('ObtenerNotificacionPorID', [id])
    if not result:
        return jsonify({'message': 'Notification not found'}), 404
    call_procedure('EliminarNotificacion', [id])
    return '', 204
