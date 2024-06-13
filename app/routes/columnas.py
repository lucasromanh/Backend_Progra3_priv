from flask import Blueprint, request, jsonify
from ..models import db, Columna
from app.routes.auth import token_required
from ..schemas import ColumnaSchema

columnas_bp = Blueprint('columnas', __name__)

columna_schema = ColumnaSchema()
columnas_schema = ColumnaSchema(many=True)

@columnas_bp.route('/columnas', methods=['GET'])
@token_required
def get_columnas(current_user):
    columnas = Columna.query.all()
    return columnas_schema.jsonify(columnas), 200

@columnas_bp.route('/columnas', methods=['POST'])
@token_required
def create_columna(current_user):
    data = request.get_json()
    errors = columna_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    columna = Columna(
        ProyectoID=data['ProyectoID'],
        ColumnaNombre=data['ColumnaNombre']
    )
    db.session.add(columna)
    db.session.commit()
    return columna_schema.jsonify(columna), 201
