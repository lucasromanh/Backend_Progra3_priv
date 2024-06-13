from flask import Blueprint, jsonify
from ..models import db, AuditLog
from app.routes.auth import token_required
from ..schemas import AuditLogSchema

auditoria_bp = Blueprint('auditoria', __name__)

audit_log_schema = AuditLogSchema()
audit_logs_schema = AuditLogSchema(many=True)

@auditoria_bp.route('/auditoria', methods=['GET'])
@token_required
def get_audit_logs(current_user):
    """
    Get All Audit Logs
    ---
    tags:
      - auditoria
    responses:
      200:
        description: List of audit logs
        schema:
          type: array
          items:
            $ref: '#/definitions/AuditLog'
    """
    logs = AuditLog.query.all()
    return audit_logs_schema.jsonify(logs), 200
