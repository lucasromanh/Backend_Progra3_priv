from flask import Blueprint, request, jsonify
from ..models import db, Proyecto
from app.routes.auth import token_required
from ..schemas import ProyectoSchema

proyectos_bp = Blueprint('proyectos', __name__)

proyecto_schema = ProyectoSchema()
proyectos_schema = ProyectoSchema(many=True)

@proyectos_bp.route('/proyectos', methods=['GET'])
@token_required
def get_proyectos(current_user):
    proyectos = Proyecto.query.all()
    return proyectos_schema.jsonify(proyectos), 200

@proyectos_bp.route('/proyectos', methods=['POST'])
@token_required
def create_proyecto(current_user):
    data = request.get_json()
    errors = proyecto_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    proyecto = Proyecto(
        BoardID=data['BoardID'],
        Titulo=data['Titulo']
    )
    db.session.add(proyecto)
    db.session.commit()
    return proyecto_schema.jsonify(proyecto), 201
