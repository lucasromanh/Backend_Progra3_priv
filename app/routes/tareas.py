from flask import Blueprint, request, jsonify
from flask_socketio import emit
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import TareaSchema, MiembroSchema, EtiquetaSchema, ChecklistSchema, FechaSchema, AdjuntoSchema, PortadaSchema
from .. import socketio
from ..constants import TASK_NOT_FOUND

tareas_bp = Blueprint('tareas', __name__)

tarea_schema = TareaSchema()
tareas_schema = TareaSchema(many=True)
miembro_schema = MiembroSchema()
etiqueta_schema = EtiquetaSchema()
checklist_schema = ChecklistSchema()
fecha_schema = FechaSchema()
adjunto_schema = AdjuntoSchema()
portada_schema = PortadaSchema()

@tareas_bp.route('/tareas', methods=['GET'])
@token_required
def get_tareas(current_user):
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

@tareas_bp.route('/tareas/<id>', methods=['GET'])
@token_required
def get_tarea(current_user, id):
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
def create_tarea(current_user):
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

@tareas_bp.route('/tareas/<id>', methods=['PUT'])
@token_required
def update_tarea(current_user, id):
    """
    Update a Task
    ---
    tags:
      - tareas
    parameters:
      - in: path
        name: id
        type: string
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
    print("Datos recibidos para actualización:", data)  
    errors = tarea_schema.validate(data)
    if errors:
        print(errors) 
        return jsonify(errors), 400

    result = call_procedure('ObtenerTareaPorID', [id])
    if not result:
        return jsonify({'message': TASK_NOT_FOUND}), 404

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

@tareas_bp.route('/tareas/<id>', methods=['DELETE'])
@token_required
def delete_tarea(current_user, id):
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
        return jsonify({'message': TASK_NOT_FOUND}), 404
    call_procedure('EliminarTarea', [id])
    emit('delete_task', {'task_id': id}, broadcast=True)
    return '', 204

# Nuevas rutas
@tareas_bp.route('/tareas/<id>/miembros', methods=['POST'])
@token_required
def add_member(current_user, id):
    """
    Add a Member to a Task
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
          id: AddMember
          required:
            - UsuarioID
          properties:
            UsuarioID:
              type: integer
    responses:
      200:
        description: Member added successfully
        schema:
          $ref: '#/definitions/Miembro'
      400:
        description: Invalid input
      404:
        description: Task not found
    """
    data = request.get_json()
    errors = miembro_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    result = call_procedure('ObtenerTareaPorID', [id])
    if not result:
        return jsonify({'message': TASK_NOT_FOUND}), 404
    call_procedure('AñadirMiembro', [
        id,
        data['UsuarioID']
    ])
    return jsonify({'message': 'Member added successfully'}), 200

@tareas_bp.route('/tareas/<id>/etiquetas', methods=['POST'])
@token_required
def add_label(current_user, id):
    """
    Add a Label to a Task
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
          id: AddLabel
          required:
            - Nombre
          properties:
            Nombre:
              type: string
    responses:
      200:
        description: Label added successfully
        schema:
          $ref: '#/definitions/Etiqueta'
      400:
        description: Invalid input
      404:
        description: Task not found
    """
    data = request.get_json()
    errors = etiqueta_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    result = call_procedure('ObtenerTareaPorID', [id])
    if not result:
        return jsonify({'message': TASK_NOT_FOUND}), 404
    call_procedure('AñadirEtiqueta', [
        id,
        data['Nombre']
    ])
    return jsonify({'message': 'Label added successfully'}), 200

@tareas_bp.route('/tareas/<id>/checklist', methods=['POST'])
@token_required
def add_checklist(current_user, id):
    """
    Add a Checklist to a Task
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
          id: AddChecklist
          required:
            - Titulo
          properties:
            Titulo:
              type: string
    responses:
      200:
        description: Checklist added successfully
        schema:
          $ref: '#/definitions/Checklist'
      400:
        description: Invalid input
      404:
        description: Task not found
    """
    data = request.get_json()
    errors = checklist_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    result = call_procedure('ObtenerTareaPorID', [id])
    if not result:
        return jsonify({'message': TASK_NOT_FOUND}), 404
    call_procedure('AñadirChecklist', [
        id,
        data['Titulo']
    ])
    return jsonify({'message': 'Checklist added successfully'}), 200

@tareas_bp.route('/tareas/<id>/fechas', methods=['POST'])
@token_required
def add_due_date(current_user, id):
    """
    Add a Due Date to a Task
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
          id: AddDueDate
          required:
            - FechaVencimiento
          properties:
            FechaVencimiento:
              type: string
              format: date
    responses:
      200:
        description: Due Date added successfully
        schema:
          $ref: '#/definitions/Fecha'
      400:
        description: Invalid input
      404:
        description: Task not found
    """
    data = request.get_json()
    errors = fecha_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    result = call_procedure('ObtenerTareaPorID', [id])
    if not result:
        return jsonify({'message': TASK_NOT_FOUND}), 404
    call_procedure('AñadirFecha', [
        id,
        data['FechaVencimiento']
    ])
    return jsonify({'message': 'Due Date added successfully'}), 200

@tareas_bp.route('/tareas/<id>/adjuntos', methods=['POST'])
@token_required
def add_attachment(current_user, id):
    """
    Add an Attachment to a Task
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
          id: AddAttachment
          required:
            - Archivo
          properties:
            Archivo:
              type: string
              format: binary
    responses:
      200:
        description: Attachment added successfully
        schema:
          $ref: '#/definitions/Adjunto'
      400:
        description: Invalid input
      404:
        description: Task not found
    """
    data = request.get_json()
    errors = adjunto_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    result = call_procedure('ObtenerTareaPorID', [id])
    if not result:
        return jsonify({'message': 'Task not found'}), 404
    call_procedure('AñadirAdjunto', [
        id,
        data['Archivo']
    ])
    return jsonify({'message': 'Attachment added successfully'}), 200

@tareas_bp.route('/tareas/<id>/portada', methods=['POST'])
@token_required
def add_cover(current_user, id):
    """
    Add a Cover to a Task
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
          id: AddCover
          required:
            - PortadaID
          properties:
            PortadaID:
              type: integer
    responses:
      200:
        description: Cover added successfully
        schema:
          $ref: '#/definitions/Portada'
      400:
        description: Invalid input
      404:
        description: Task not found
    """
    data = request.get_json()
    errors = portada_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    result = call_procedure('ObtenerTareaPorID', [id])
    if not result:
        return jsonify({'message': 'Task not found'}), 404
    call_procedure('AñadirPortada', [
        id,
        data['PortadaID']
    ])
    return jsonify({'message': 'Cover added successfully'}), 200

@tareas_bp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@tareas_bp.route('/test', methods=['OPTIONS', 'GET', 'PUT', 'POST', 'DELETE'])
def test():
    response = jsonify({'message': 'This is a test response'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
