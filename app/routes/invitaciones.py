from flask import Blueprint, request, jsonify
from ..models import db, Invitacion
from app.routes.auth import token_required
from ..schemas import InvitacionSchema

invitaciones_bp = Blueprint('invitaciones', __name__)

invitacion_schema = InvitacionSchema()
invitaciones_schema = InvitacionSchema(many=True)

@invitaciones_bp.route('/invitaciones', methods=['GET'])
@token_required
def get_invitaciones(current_user):
    invitaciones = Invitacion.query.all()
    return invitaciones_schema.jsonify(invitaciones), 200

@invitaciones_bp.route('/invitaciones', methods=['POST'])
@token_required
def create_invitacion(current_user):
    data = request.get_json()
    errors = invitacion_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    invitacion = Invitacion(
        UsuarioOrigenID=current_user.UsuarioID,
        UsuarioDestinoID=data['UsuarioDestinoID'],
        Estado='pendiente',
        FechaEnvio=db.func.current_timestamp()
    )
    db.session.add(invitacion)
    db.session.commit()
    return invitacion_schema.jsonify(invitacion), 201
