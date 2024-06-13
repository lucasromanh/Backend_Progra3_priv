from flask import Blueprint, request, jsonify
from ..models import db, AsignacionTarea
from app.routes.auth import token_required
from ..schemas import AsignacionTareaSchema

asignaciones_bp = Blueprint('asignaciones', __name__)

asignacion_schema = AsignacionTareaSchema()
asignaciones_schema = AsignacionTareaSchema(many=True)

@asignaciones_bp.route('/asignaciones', methods=['GET'])
@token_required
def get_asignaciones(current_user):
    asignaciones = AsignacionTarea.query.all()
    return asignaciones_schema.jsonify(asignaciones), 200

@asignaciones_bp.route('/asignaciones', methods=['POST'])
@token_required
def create_asignacion(current_user):
    data = request.get_json()
    errors = asignacion_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    asignacion = AsignacionTarea(
        TareaID=data['TareaID'],
        UsuarioID=data['UsuarioID']
    )
    db.session.add(asignacion)
    db.session.commit()
    return asignacion_schema.jsonify(asignacion), 201
