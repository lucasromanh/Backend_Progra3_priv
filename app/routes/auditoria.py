from flask import Blueprint, jsonify
from ..utils import call_procedure
from app.routes.auth import token_required
from ..schemas import AuditLogSchema

auditoria_bp = Blueprint('auditoria', __name__)

audit_log_schema = AuditLogSchema()
audit_logs_schema = AuditLogSchema(many=True)

@auditoria_bp.route('/auditoria', methods=['GET'])
@token_required
def get_audit_logs(current_user):
    """
    Obtener todos los registros de auditoría.
    ---
    tags:
      - auditoria
    responses:
      200:
        description: Lista de registros de auditoría.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/AuditLog'
    """
    logs = call_procedure('ObtenerTodosLosRegistrosDeAuditoria', [])
    return jsonify({'logs': audit_logs_schema.dump(logs)}), 200
