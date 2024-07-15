from flask import Blueprint, request, jsonify, current_app as app
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import AdjuntoSchema
from ..constants import FILE_NOT_FOUND, INVALID_FILE

adjuntos_bp = Blueprint('adjuntos', __name__)

adjunto_schema = AdjuntoSchema()
adjuntos_schema = AdjuntoSchema(many=True)

@adjuntos_bp.route('/tareas/<int:tarea_id>/adjuntos', methods=['POST'])
@token_required
def upload_adjunto(current_user, tarea_id):
    """
    Subir un adjunto a una tarea
    ---
    tags:
      - adjuntos
    parameters:
      - in: formData
        name: file
        type: file
        required: true
    responses:
      201:
        description: Adjunto cargado exitosamente
        schema:
          $ref: '#/definitions/Adjunto'
      400:
        description: Entrada inválida
    """
    if 'file' not in request.files:
        return jsonify({'message': 'No se encontró el archivo'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No se seleccionó ningún archivo'}), 400
    filename = secure_filename(file.filename)
    try:
        result = call_procedure('upload_attachment', [current_user.id, tarea_id, filename, file.read()])
        if result is None:
            raise ValueError('Error al cargar el archivo')
        return jsonify({'message': 'Archivo cargado exitosamente', 'id': result[0]}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@adjuntos_bp.route('/tareas/<int:tarea_id>/adjuntos', methods=['GET'])
@token_required
def get_adjuntos(current_user, tarea_id):
    """
    Obtener todos los adjuntos de una tarea
    """
    try:
        adjuntos = call_procedure('get_all_attachments', [tarea_id])
        return jsonify({'adjuntos': adjuntos_schema.dump(adjuntos)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@adjuntos_bp.route('/tareas/<int:tarea_id>/adjuntos/<int:adjunto_id>', methods=['PUT'])
@token_required
def update_adjunto(current_user, tarea_id, adjunto_id):
    """
    Actualizar un adjunto específico
    """
    new_data = request.json
    try:
        result = call_procedure('update_attachment', [adjunto_id, new_data['filename'], new_data['file_data']])
        if result is None:
            raise ValueError('Error al actualizar el adjunto')
        return jsonify({'message': 'Adjunto actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@adjuntos_bp.route('/tareas/<int:tarea_id>/adjuntos/<int:adjunto_id>', methods=['DELETE'])
@token_required
def delete_adjunto(current_user, tarea_id, adjunto_id):
    """
    Eliminar un adjunto específico
    """
    try:
        result = call_procedure('delete_attachment', [adjunto_id])
        if result is None:
            raise ValueError('Error al eliminar el adjunto')
        return jsonify({'message': 'Adjunto eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
