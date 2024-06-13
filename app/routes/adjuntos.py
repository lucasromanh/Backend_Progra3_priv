from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import AdjuntoSchema

adjuntos_bp = Blueprint('adjuntos', __name__)

adjunto_schema = AdjuntoSchema()
adjuntos_schema = AdjuntoSchema(many=True)

@adjuntos_bp.route('/tareas/<int:tarea_id>/adjuntos', methods=['POST'])
@token_required
def upload_adjunto(tarea_id):
    """
    Upload Attachment to Task
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
        description: Attachment uploaded successfully
        schema:
          $ref: '#/definitions/Adjunto'
      400:
        description: Invalid input
    """
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)
        call_procedure('CrearAdjunto', [
            tarea_id,
            filepath
        ])
        return jsonify({'message': 'Attachment uploaded successfully'}), 201

@adjuntos_bp.route('/adjuntos/<int:id>', methods=['GET'])
@token_required
def get_adjunto(id):
    """
    Get an Attachment by ID
    ---
    tags:
      - adjuntos
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the attachment
    responses:
      200:
        description: Attachment found
        schema:
          $ref: '#/definitions/Adjunto'
      404:
        description: Attachment not found
    """
    result = call_procedure('ObtenerAdjuntoPorID', [id])
    if not result:
        return jsonify({'message': 'Attachment not found'}), 404
    return jsonify(result[0]), 200

@adjuntos_bp.route('/adjuntos/<int:id>', methods=['DELETE'])
@token_required
def delete_adjunto(id):
    """
    Delete an Attachment
    ---
    tags:
      - adjuntos
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID of the attachment
    responses:
      204:
        description: Attachment deleted successfully
      404:
        description: Attachment not found
    """
    result = call_procedure('ObtenerAdjuntoPorID', [id])
    if not result:
        return jsonify({'message': 'Attachment not found'}), 404
    call_procedure('EliminarAdjunto', [id])
    return '', 204
