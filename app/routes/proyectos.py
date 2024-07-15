from flask import Blueprint, request, jsonify
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import ProyectoSchema

proyectos_bp = Blueprint('proyectos', __name__)

proyecto_schema = ProyectoSchema()
proyectos_schema = ProyectoSchema(many=True)

@proyectos_bp.route('/proyectos', methods=['GET'])
@token_required
def get_proyectos(current_user):
    """
    Obtener todos los proyectos.
    ---
    tags:
      - proyectos
    responses:
      200:
        description: Devuelve un listado de todos los proyectos.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Proyecto'
    """
    result = call_procedure('ObtenerTodosLosProyectos', [])
    return jsonify({'proyectos': proyectos_schema.dump(result)}), 200

@proyectos_bp.route('/proyectos/<int:id>', methods=['GET'])
@token_required
def get_proyecto(id):
    """
    Obtener detalles de un proyecto específico por su ID.
    ---
    tags:
      - proyectos
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del proyecto a obtener.
    responses:
      200:
        description: Devuelve el proyecto especificado.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Proyecto'
      404:
        description: El proyecto especificado no fue encontrado.
    """
    result = call_procedure('ObtenerProyectoPorID', [id])
    if not result:
        return jsonify({'message': 'Proyecto no encontrado'}), 404
    return jsonify({'proyecto': proyecto_schema.dump(result[0])}), 200

@proyectos_bp.route('/proyectos', methods=['POST'])
@token_required
def create_proyecto(current_user):
    """
    Crear un nuevo proyecto.
    ---
    tags:
      - proyectos
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              BoardID:
                type: integer
                description: ID del tablero al que pertenece el proyecto.
              Titulo:
                type: string
                description: Título del nuevo proyecto.
    responses:
      201:
        description: Proyecto creado exitosamente.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Proyecto'
      400:
        description: Entrada inválida.
    """
    data = request.get_json()
    errors = proyecto_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    proyecto_id = call_procedure('CrearProyecto', [
        data['BoardID'],
        data['Titulo']
    ])
    return jsonify({'message': 'Proyecto creado exitosamente', 'id': proyecto_id}), 201

@proyectos_bp.route('/proyectos/<int:id>', methods=['PUT'])
@token_required
def update_proyecto(id):
    """
    Actualizar un proyecto existente.
    ---
    tags:
      - proyectos
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del proyecto a actualizar.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              BoardID:
                type: integer
                description: ID del tablero al que pertenece el proyecto.
              Titulo:
                type: string
                description: Nuevo título para el proyecto.
    responses:
      200:
        description: Proyecto actualizado exitosamente.
      400:
        description: Entrada inválida.
      404:
        description: Proyecto no encontrado.
    """
    data = request.get_json()
    errors = proyecto_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    if not call_procedure('VerificarProyectoExistente', [id]):
        return jsonify({'message': 'Proyecto no encontrado'}), 404
    call_procedure('ActualizarProyecto', [
        id,
        data['BoardID'],
        data['Titulo']
    ])
    return jsonify({'message': 'Proyecto actualizado exitosamente'}), 200

@proyectos_bp.route('/proyectos/<int:id>', methods=['DELETE'])
@token_required
def delete_proyecto(id):
    """
    Eliminar un proyecto existente.
    ---
    tags:
      - proyectos
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del proyecto a eliminar.
    responses:
      204:
        description: Proyecto eliminado exitosamente.
      404:
        description: Proyecto no encontrado.
    """
    if not call_procedure('VerificarProyectoExistente', [id]):
        return jsonify({'message': 'Proyecto no encontrado'}), 404
    call_procedure('EliminarProyecto', [id])
    return '', 204
