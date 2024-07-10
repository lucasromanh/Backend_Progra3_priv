from flask import Blueprint

api_bp = Blueprint('api', __name__)

from .auth import auth_bp
from .usuarios import usuarios_bp
from .perfiles import perfiles_bp
from .invitaciones import invitaciones_bp
from .boards import boards_bp
from .proyectos import proyectos_bp
from .tareas import tareas_bp
from .columnas import columnas_bp
from .asignaciones import asignaciones_bp

api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(usuarios_bp)
api_bp.register_blueprint(perfiles_bp)
api_bp.register_blueprint(invitaciones_bp)
api_bp.register_blueprint(boards_bp)
api_bp.register_blueprint(proyectos_bp)
api_bp.register_blueprint(tareas_bp)
api_bp.register_blueprint(columnas_bp)
api_bp.register_blueprint(asignaciones_bp)
