from flask import Blueprint, request, jsonify
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import InvitacionSchema
from app import db


invitaciones_bp = Blueprint('invitaciones', __name__)

invitacion_schema = InvitacionSchema()
invitaciones_schema = InvitacionSchema(many=True)

@invitaciones_bp.route('/usuarios/id', methods=['POST'])
@token_required
def get_user_id(current_user):
    """
    Obtener el ID de un usuario basado en su email.
    ---
    tags:
      - usuarios
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                description: Email del usuario
    responses:
      200:
        description: Devuelve el ID del usuario
        content:
          application/json:
            schema:
              type: object
              properties:
                UsuarioID:
                  type: integer
                  description: ID del usuario
      404:
        description: Usuario no encontrado
    """
    data = request.get_json()
    email = data.get('email')
    user = call_procedure('ObtenerUsuarioPorCorreoElectronico', [email])
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    return jsonify({'UsuarioID': user[0]['UsuarioID']}), 200


@invitaciones_bp.route('/invitaciones', methods=['GET'])
@token_required
def get_invitaciones(current_user):
    """
    Obtener todas las invitaciones.
    ---
    tags:
      - invitaciones
    responses:
      200:
        description: Devuelve un listado de todas las invitaciones.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Invitacion'
    """
    result = call_procedure('ObtenerTodasLasInvitaciones', [])
    
    # Para cada invitación, obtener el correo electrónico del destinatario
    for invitacion in result:
        usuario_destino = call_procedure('ObtenerUsuarioPorID', [invitacion['UsuarioDestinoID']])
        if usuario_destino:
            invitacion['email'] = usuario_destino[0]['CorreoElectronico']
    
    return jsonify({'invitaciones': result}), 200

@invitaciones_bp.route('/invitaciones/<int:id>', methods=['GET'])
@token_required
def get_invitacion(id):
    """
    Obtener detalles de una invitación específica por su ID.
    ---
    tags:
      - invitaciones
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la invitación a obtener.
    responses:
      200:
        description: Devuelve la invitación especificada.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Invitacion'
      404:
        description: La invitación especificada no fue encontrada.
    """
    result = call_procedure('ObtenerInvitacionPorID', [id])
    if not result:
        return jsonify({'message': 'Invitación no encontrada'}), 404
    return jsonify({'invitacion': invitacion_schema.dump(result[0])}), 200

@invitaciones_bp.route('/invitaciones', methods=['POST'])
@token_required
def create_invitacion(current_user):
    """
    Crear una nueva invitación.
    ---
    tags:
      - invitaciones
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              UsuarioDestinoID:
                type: integer
                description: ID del usuario al que se envía la invitación.
    responses:
      201:
        description: Invitación creada exitosamente.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Invitacion'
      400:
        description: Entrada inválida.
    """
    data = request.get_json()
    errors = invitacion_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    invitacion_id = call_procedure('CrearInvitacion', [
        current_user.UsuarioID,  # Usar el ID del usuario actual desde el token
        data['UsuarioDestinoID'],
        'pendiente'
    ])
    # Crear notificación para el usuario destinatario
    call_procedure('CrearNotificacion', [
        data['UsuarioDestinoID'],
        f'Has recibido una nueva invitación de {current_user.UsuarioID}',
        False
    ])
    return jsonify({'message': 'Invitación creada exitosamente', 'id': invitacion_id}), 201




@invitaciones_bp.route('/invitaciones/<int:id>', methods=['PUT'])
@token_required
def update_invitacion(id):
    """
    Actualizar una invitación existente.
    ---
    tags:
      - invitaciones
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la invitación a actualizar.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              Estado:
                type: string
                description: Nuevo estado de la invitación.
    responses:
      200:
        description: Invitación actualizada exitosamente.
      400:
        description: Entrada inválida.
      404:
        description: Invitación no encontrada.
    """
    data = request.get_json()
    estado = data.get('Estado')
    if not estado:
        return jsonify({'message': 'Datos insuficientes para actualizar la invitación'}), 400
    if not call_procedure('VerificarInvitacionExistente', [id]):
        return jsonify({'message': 'Invitación no encontrada'}), 404
    call_procedure('ActualizarInvitacion', [id, estado])
    return jsonify({'message': 'Invitación actualizada exitosamente'}), 200

@invitaciones_bp.route('/invitaciones/aceptar/<int:id>', methods=['POST'])
@token_required
def accept_invitation(current_user, id):
    """
    Aceptar una invitación.
    ---
    tags:
      - invitaciones
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la invitación a aceptar.
    responses:
      200:
        description: Invitación aceptada exitosamente.
      404:
        description: Invitación no encontrada.
    """
    if not call_procedure('VerificarInvitacionExistente', [id]):
        return jsonify({'message': 'Invitación no encontrada'}), 404
    call_procedure('AceptarInvitacion', [id])
    return jsonify({'message': 'Invitación aceptada exitosamente'}), 200

@invitaciones_bp.route('/invitaciones/<int:id>', methods=['DELETE'])
@token_required
def delete_invitacion(current_user, id):
    """
    Eliminar una invitación existente.
    ---
    tags:
      - invitaciones
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la invitación a eliminar.
    responses:
      204:
        description: Invitación eliminada exitosamente.
      404:
        description: Invitación no encontrada.
    """
    if not call_procedure('VerificarInvitacionExistente', [id]):
        return jsonify({'message': 'Invitación no encontrada'}), 404
    call_procedure('EliminarInvitacion', [id])
    return '', 204

@invitaciones_bp.route('/invitaciones/recibidas', methods=['GET'])
@token_required
def get_invitaciones_recibidas(current_user):
    """
    Obtener todas las invitaciones recibidas.
    ---
    tags:
      - invitaciones
    responses:
      200:
        description: Devuelve un listado de todas las invitaciones recibidas.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Invitacion'
    """
    invitaciones = call_procedure('ObtenerInvitacionesRecibidas', [current_user.UsuarioID])
    return jsonify({'invitacionesRecibidas': invitaciones_schema.dump(invitaciones)}), 200

@invitaciones_bp.route('/invitaciones/aceptadas', methods=['GET'])
@token_required
def get_invitaciones_aceptadas(current_user):
    """
    Obtener todas las invitaciones aceptadas.
    ---
    tags:
      - invitaciones
    responses:
      200:
        description: Devuelve un listado de todas las invitaciones aceptadas.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Invitacion'
    """
    invitaciones = call_procedure('ObtenerInvitacionesAceptadas', [current_user.UsuarioID])
    return jsonify({'invitacionesAceptadas': invitaciones_schema.dump(invitaciones)}), 200
