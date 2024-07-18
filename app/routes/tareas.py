from flask import Blueprint, request, jsonify, current_app as app
from flask_socketio import emit
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Tarea
from ..utils import call_procedure, obtener_todas_las_tareas, obtener_tarea_por_id
from app.routes.auth import token_required
from ..schemas import TareaSchema, MiembroSchema, EtiquetaSchema, ChecklistSchema, FechaSchema, AdjuntoSchema, PortadaSchema
from .. import socketio
from ..constants import TASK_NOT_FOUND
from marshmallow import ValidationError

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
    tasks = obtener_todas_las_tareas()
    if not tasks:
        return jsonify({'message': 'No tasks found'}), 404
    
    formatted_tasks = []
    for task in tasks:
        formatted_tasks.append({
            "id": task['TareaID'],
            "board_id": task['ProyectoID'],
            "title": task['Titulo'],
            "description": task['Descripcion'],
            "status": task['Estado'],
            "due_date": task['FechaVencimiento'].isoformat() if task['FechaVencimiento'] else None,
            "created_at": task['FechaCreacion'].isoformat() if task['FechaCreacion'] else None,
            "updated_at": task['UltimaActualizacion'].isoformat() if task['UltimaActualizacion'] else None
        })
    return jsonify(formatted_tasks), 200
  
@tareas_bp.route('/tareas/<int:id>', methods=['GET'])
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
    tasks = obtener_todas_las_tareas()
    if not tasks:
        return jsonify({'message': 'No tasks found'}), 404
    
    formatted_tasks = []
    for task in tasks:
        formatted_tasks.append({
            "id": task['TareaID'],
            "board_id": task['ProyectoID'],
            "title": task['Titulo'],
            "description": task['Descripcion'],
            "status": task['Estado'],
            "due_date": task['FechaVencimiento'].isoformat() if task['FechaVencimiento'] else None,
            "created_at": task['FechaCreacion'].isoformat() if task['FechaCreacion'] else None,
            "updated_at": task['UltimaActualizacion'].isoformat() if task['UltimaActualizacion'] else None
        })
    return jsonify(formatted_tasks), 200

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
    app.logger.info(f"User creating task: {current_user.UsuarioID}")
    app.logger.info(f"Data received: {data}") 

    errors = tarea_schema.validate(data)
    if errors:
        app.logger.error(f"Validation errors: {errors}")  
        return jsonify(errors), 400
    try:
        result = call_procedure('CrearTarea', [
            data['ProyectoID'],
            data['Titulo'],
            data.get('Descripcion', ''),
            data.get('Importancia', 1),
            data.get('Estado', 'pendiente'),
            data.get('FechaVencimiento', None)
        ])
        app.logger.info(f"Result from CrearTarea: {result}") 
        new_task_id = result[0][0]
        new_task = {
            'id': new_task_id,
            'ProyectoID': data['ProyectoID'],
            'Titulo': data['Titulo'],
            'Descripcion': data.get('Descripcion', ''),
            'Importancia': data.get('Importancia', 1),
            'Estado': data.get('Estado', 'pendiente'),
            'FechaVencimiento': data.get('FechaVencimiento', None)
        }
        socketio.emit('new_task', {'task': new_task}, namespace='/')
        return jsonify({'message': 'Task created successfully', 'task': new_task}), 201
    except Exception as e:
        app.logger.error(f"Error creating task: {e}")  
        return jsonify({'message': 'Internal server error'}), 500

@tareas_bp.route('/tareas/<int:id>', methods=['PUT'])
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
    app.logger.info(f"Datos recibidos para actualización: {data}")

    data.pop('id', None)
    data.pop('columnId', None)
    data.pop('message', None)

    # Validar datos
    try:
        tarea_data = tarea_schema.load(data, partial=True)
        tarea_data_dict = tarea_schema.dump(tarea_data)
        app.logger.info(f"Datos validados: {tarea_data_dict}")
    except ValidationError as err:
        app.logger.error(f"Errores de validación: {err.messages}")
        return jsonify(err.messages), 400

    try:
        tarea_id = int(id)
    except ValueError:
        app.logger.error(f"ID de tarea inválido: {id}")
        return jsonify({'message': 'Invalid task ID'}), 400

    result = call_procedure('ObtenerTareaPorID', [tarea_id])
    if not result or not result[0]:
        app.logger.error(f"Tarea no encontrada o datos incompletos para la tarea: {result}")
        return jsonify({'message': TASK_NOT_FOUND}), 404

    tarea_actual = result[0]
    app.logger.info(f"Tarea actual obtenida: {tarea_actual}")
    
    tarea_data_dict['ProyectoID'] = tarea_data_dict.get('ProyectoID', tarea_actual[1])
    tarea_data_dict['Titulo'] = tarea_data_dict.get('Titulo', tarea_actual[2])
    tarea_data_dict['Descripcion'] = tarea_data_dict.get('Descripcion', tarea_actual[3])
    tarea_data_dict['Importancia'] = tarea_data_dict.get('Importancia', tarea_actual[4])
    tarea_data_dict['Estado'] = tarea_data_dict.get('Estado', tarea_actual[5])
    tarea_data_dict['FechaVencimiento'] = tarea_data_dict.get('FechaVencimiento', tarea_actual[6])

    if tarea_data_dict['ProyectoID'] is None:
        tarea_data_dict['ProyectoID'] = tarea_actual[1]
    if tarea_data_dict['Titulo'] is None:
        tarea_data_dict['Titulo'] = tarea_actual[2]
    if tarea_data_dict['Descripcion'] is None:
        tarea_data_dict['Descripcion'] = tarea_actual[3]
    if tarea_data_dict['Importancia'] is None:
        tarea_data_dict['Importancia'] = tarea_actual[4]
    if tarea_data_dict['Estado'] is None:
        tarea_data_dict['Estado'] = tarea_actual[5]
    if tarea_data_dict['FechaVencimiento'] is None:
        tarea_data_dict['FechaVencimiento'] = tarea_actual[6]

    if isinstance(tarea_data_dict['Importancia'], str):
        try:
            tarea_data_dict['Importancia'] = int(tarea_data_dict['Importancia'])
        except ValueError:
            tarea_data_dict['Importancia'] = 1 

    # Actualizar tarea
    try:
        call_procedure('ActualizarTarea', [
            tarea_id,
            tarea_data_dict['ProyectoID'],
            tarea_data_dict['Titulo'],
            tarea_data_dict['Descripcion'],
            tarea_data_dict['Importancia'],
            tarea_data_dict['Estado'],
            tarea_data_dict['FechaVencimiento']
        ])
        app.logger.info(f"Tarea actualizada correctamente: {tarea_id}")
    except Exception as e:
        app.logger.error(f"Error al actualizar la tarea: {e}")
        return jsonify({'message': 'Internal server error'}), 500

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
    socketio.emit('delete_task', {'task_id': id}, namespace='/')
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
