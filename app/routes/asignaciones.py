from flask import Blueprint, request, jsonify
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import AsignacionTareaSchema

asignaciones_bp = Blueprint('asignaciones', __name__)

asignacion_schema = AsignacionTareaSchema()
asignaciones_schema = AsignacionTareaSchema(many=True)

@asignaciones_bp.route('/asignaciones', methods=['GET'])
@token_required
def get_asignaciones(current_user):
    """
    Obtener todas las asignaciones de tareas.
    ---
    tags:
      - asignaciones
    responses:
      200:
        description: Devuelve un listado de todas las asignaciones.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/AsignacionTarea'
    """
    asignaciones = call_procedure('ObtenerTodasLasAsignaciones', [])
    return jsonify({'asignaciones': asignaciones_schema.dump(asignaciones)}), 200

@asignaciones_bp.route('/asignaciones/<int:id>', methods=['GET'])
@token_required
def get_asignacion(id):
    """
    Obtener detalles de una asignación específica por su ID.
    ---
    tags:
      - asignaciones
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la asignación a obtener.
    responses:
      200:
        description: Devuelve la asignación especificada.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AsignacionTarea'
      404:
        description: La asignación especificada no fue encontrada.
    """
    asignacion = call_procedure('ObtenerAsignacionPorID', [id])
    if not asignacion:
        return jsonify({'message': 'Asignación no encontrada'}), 404
    return jsonify({'asignacion': asignacion_schema.dump(asignacion)}), 200

@asignaciones_bp.route('/asignaciones', methods=['POST'])
@token_required
def create_asignacion(current_user):
    """
    Crear una nueva asignación de tarea.
    ---
    tags:
      - asignaciones
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              TareaID:
                type: integer
                description: ID de la tarea a asignar.
              UsuarioID:
                type: integer
                description: ID del usuario asignado a la tarea.
    responses:
      201:
        description: Asignación creada exitosamente.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AsignacionTarea'
      400:
        description: Entrada inválida.
    """
    data = request.get_json()
    tarea_id = data.get('TareaID')
    usuario_id = data.get('UsuarioID')
    if not tarea_id or not usuario_id:
        return jsonify({'message': 'Datos insuficientes para crear una asignación'}), 400
    asignacion_id = call_procedure('CrearAsignacion', [tarea_id, usuario_id])
    return jsonify({'message': 'Asignación creada exitosamente', 'id': asignacion_id}), 201

@asignaciones_bp.route('/asignaciones/<int:id>', methods=['PUT'])
@token_required
def update_asignacion(id):
    """
    Actualizar una asignación existente.
    ---
    tags:
      - asignaciones
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la asignación a actualizar.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              TareaID:
                type: integer
                description: Nuevo ID de la tarea asignada.
              UsuarioID:
                type: integer
                description: Nuevo ID del usuario asignado.
    responses:
      200:
        description: Asignación actualizada exitosamente.
      400:
        description: Entrada inválida.
      404:
        description: Asignación no encontrada.
    """
    data = request.get_json()
    tarea_id = data.get('TareaID')
    usuario_id = data.get('UsuarioID')
    if not tarea_id or not usuario_id:
        return jsonify({'message': 'Datos insuficientes para actualizar la asignación'}), 400
    if not call_procedure('VerificarAsignacionExistente', [id]):
        return jsonify({'message': 'Asignación no encontrada'}), 404
    call_procedure('ActualizarAsignacion', [id, tarea_id, usuario_id])
    return jsonify({'message': 'Asignación actualizada exitosamente'}), 200

@asignaciones_bp.route('/asignaciones/<int:id>', methods=['DELETE'])
@token_required
def delete_asignacion(id):
    """
    Eliminar una asignación existente.
    ---
    tags:
      - asignaciones
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID de la asignación a eliminar.
    responses:
      204:
        description: Asignación eliminada exitosamente.
      404:
        description: Asignación no encontrada.
    """
    if not call_procedure('VerificarAsignacionExistente', [id]):
        return jsonify({'message': 'Asignación no encontrada'}), 404
    call_procedure('EliminarAsignacion', [id])
    return '', 204
