from flask import Blueprint, request, jsonify
from ..models import db, Board
from app.routes.auth import token_required
from ..schemas import BoardSchema

boards_bp = Blueprint('boards', __name__)

board_schema = BoardSchema()
boards_schema = BoardSchema(many=True)

@boards_bp.route('/boards', methods=['GET'])
@token_required
def get_boards(current_user):
    boards = Board.query.all()
    return boards_schema.jsonify(boards), 200

@boards_bp.route('/boards', methods=['POST'])
@token_required
def create_board(current_user):
    data = request.get_json()
    errors = board_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    board = Board(
        UsuarioPropietarioID=current_user.UsuarioID,
        Titulo=data['Titulo']
    )
    db.session.add(board)
    db.session.commit()
    return board_schema.jsonify(board), 201
