from flask import Blueprint, request, jsonify
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import BoardSchema

boards_bp = Blueprint('boards', __name__)

board_schema = BoardSchema()
boards_schema = BoardSchema(many=True)

@boards_bp.route('/boards', methods=['GET'])
@token_required
def get_boards(current_user):
    """
    Obtener todos los tableros.
    ---
    tags:
      - boards
    responses:
      200:
        description: Devuelve un listado de todos los tableros.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Board'
    """
    boards = call_procedure('ObtenerTodosLosTableros', [])
    return jsonify({'boards': boards_schema.dump(boards)}), 200

@boards_bp.route('/boards/<int:id>', methods=['GET'])
@token_required
def get_board(id):
    """
    Obtener detalles de un tablero específico por su ID.
    ---
    tags:
      - boards
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del tablero a obtener.
    responses:
      200:
        description: Devuelve el tablero especificado.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Board'
      404:
        description: El tablero especificado no fue encontrado.
    """
    board = call_procedure('ObtenerTableroPorID', [id])
    if not board:
        return jsonify({'message': 'Tablero no encontrado'}), 404
    return jsonify({'board': board_schema.dump(board)}), 200

@boards_bp.route('/boards', methods=['POST'])
@token_required
def create_board(current_user):
    """
    Crear un nuevo tablero.
    ---
    tags:
      - boards
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              Titulo:
                type: string
                description: Título del nuevo tablero.
    responses:
      201:
        description: Tablero creado exitosamente.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Board'
      400:
        description: Entrada inválida.
    """
    data = request.get_json()
    titulo = data.get('Titulo')
    if not titulo:
        return jsonify({'message': 'Datos insuficientes para crear un tablero'}), 400
    board_id = call_procedure('CrearTablero', [current_user.UsuarioID, titulo])
    return jsonify({'message': 'Tablero creado exitosamente', 'id': board_id}), 201

@boards_bp.route('/boards/<int:id>', methods=['PUT'])
@token_required
def update_board(id):
    """
    Actualizar un tablero existente.
    ---
    tags:
      - boards
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del tablero a actualizar.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              Titulo:
                type: string
                description: Nuevo título para el tablero.
    responses:
      200:
        description: Tablero actualizado exitosamente.
      400:
        description: Entrada inválida.
      404:
        description: Tablero no encontrado.
    """
    data = request.get_json()
    titulo = data.get('Titulo')
    if not titulo:
        return jsonify({'message': 'Datos insuficientes para actualizar el tablero'}), 400
    if not call_procedure('VerificarTableroExistente', [id]):
        return jsonify({'message': 'Tablero no encontrado'}), 404
    call_procedure('ActualizarTablero', [id, titulo])
    return jsonify({'message': 'Tablero actualizado exitosamente'}), 200

@boards_bp.route('/boards/<int:id>', methods=['DELETE'])
@token_required
def delete_board(id):
    """
    Eliminar un tablero existente.
    ---
    tags:
      - boards
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
        description: El ID del tablero a eliminar.
    responses:
      204:
        description: Tablero eliminado exitosamente.
      404:
        description: Tablero no encontrado.
    """
    if not call_procedure('VerificarTableroExistente', [id]):
        return jsonify({'message': 'Tablero no encontrado'}), 404
    call_procedure('EliminarTablero', [id])
    return '', 204
