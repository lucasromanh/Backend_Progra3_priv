from flask import Blueprint, request, jsonify
from flask_socketio import emit
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import TareaSchema
from .. import socketio
from ..constants import TASK_NOT_FOUND

tareas_bp = Blueprint('tareas', __name__)

tarea_schema = TareaSchema()
tareas_schema = TareaSchema(many=True)

@tareas_bp.route('/tareas', methods=['GET'])
@token_required
def get_tareas():
    """
    Get All Tasks
    ---
    tags:
      - tareas
    responses:
      200:
        description: List of tasks
        schema:
          type: array
          items:
            $ref: '#/definitions/Tarea'
    """
    result = call_procedure('ObtenerTareas', [])
    return jsonify(result), 200

@tareas_bp.route('/tareas/<int:id>', methods=['GET'])
@token_required
def get_tarea(id):
    """
    Get a Task by ID
    ---
    tags:
      - tareas
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the task
    responses:
      200:
        description: Task found
        schema:
          $ref: '#/definitions/Tarea'
      404:
        description: Task not found
    """
    result = call_procedure('ObtenerTareaPorID', [id])
    if not result:
        return jsonify({'message': TASK_NOT_FOUND}), 404
    return jsonify(result[0]), 200

@tareas_bp.route('/tareas', methods=['POST'])
@token_required
def create_tarea():
    """
    Create a New Task
    ---
    tags:
      - tareas
    parameters:
      - in: body
        name: body
        schema:
          id: CreateTarea
          required:
            - ProyectoID
            - Titulo
          properties:
            ProyectoID:
              type: integer
            Titulo:
              type: string
            Descripcion:
              type: string
            Importancia:
              type: integer
            Estado:
              type: string
              enum: ['pendiente', 'en_proceso', 'completada']
            FechaVencimiento:
              type: string
              format: date
    responses:
      201:
        description: Task created successfully
        schema:
          $ref: '#/definitions/Tarea'
      400:
        description: Invalid input
    """
    data = request.get_json()
    errors = tarea_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    call_procedure('CrearTarea', [
        data['ProyectoID'],
        data['Titulo'],
        data.get('Descripcion', ''),
        data.get('Importancia', 1),
        data.get('Estado', 'pendiente'),
        data.get('FechaVencimiento', None)
    ])
    emit('new_task', {'task': data}, broadcast=True)
    return jsonify({'message': 'Task created successfully'}), 201

@tareas_bp.route('/tareas/<int:id>', methods=['PUT'])
@token_required
def update_tarea(id):
    """
    Update a Task
    ---
    tags:
      - tareas
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the task
      - in: body
        name: body
        schema:
          id: UpdateTarea
          properties:
            ProyectoID:
              type: integer
            Titulo:
              type: string
            Descripcion:
              type: string
            Importancia:
              type: integer
            Estado:
              type: string
              enum: ['pendiente', 'en_proceso', 'completada']
            FechaVencimiento:
              type: string
              format: date
    responses:
      200:
        description: Task updated successfully
        schema:
          $ref: '#/definitions/Tarea'
      400:
        description: Invalid input
      404:
        description: Task not found
    """
    data = request.get_json()
    errors = tarea_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    result = call_procedure('ObtenerTareaPorID', [id])
    if not result:
        return jsonify({'message': 'Task not found'}), 404
    call_procedure('ActualizarTarea', [
        id,
        data['ProyectoID'],
        data['Titulo'],
        data.get('Descripcion', ''),
        data.get('Importancia', 1),
        data.get('Estado', 'pendiente'),
        data.get('FechaVencimiento', None)
    ])
    emit('update_task', {'task': data}, broadcast=True)
    return jsonify({'message': 'Task updated successfully'}), 200

@tareas_bp.route('/tareas/<int:id>', methods=['DELETE'])
@token_required
def delete_tarea(id):
    """
    Delete a Task
    ---
    tags:
      - tareas
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the task
    responses:
      204:
        description: Task deleted successfully
      404:
        description: Task not found
    """
    result = call_procedure('ObtenerTareaPorID', [id])
    if not result:
        return jsonify({'message': 'Task not found'}), 404
    call_procedure('EliminarTarea', [id])
    emit('delete_task', {'task_id': id}, broadcast=True)
    return '', 204
