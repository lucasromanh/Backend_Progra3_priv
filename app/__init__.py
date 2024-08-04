from flask import Flask, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
jwt = JWTManager()

def create_app(config_class='config.DevelopmentConfig'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    jwt.init_app(app)  # Inicializar JWTManager

    # Configuración CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    Swagger(app)

    from .routes.auth import auth_bp
    from .routes.usuarios import usuarios_bp
    from .routes.perfiles import perfiles_bp
    from .routes.tareas import tareas_bp
    from .routes.comentarios import comentarios_bp
    from .routes.notificaciones import notificaciones_bp
    from .routes.etiquetas import etiquetas_bp
    from .routes.adjuntos import adjuntos_bp
    from .routes.columnas import columnas_bp
    from .routes.invitaciones import invitaciones_bp
    from .routes.boards import boards_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(usuarios_bp, url_prefix='/api')
    app.register_blueprint(perfiles_bp, url_prefix='/api')
    app.register_blueprint(tareas_bp, url_prefix='/api')
    app.register_blueprint(comentarios_bp, url_prefix='/api')
    app.register_blueprint(notificaciones_bp, url_prefix='/api')
    app.register_blueprint(etiquetas_bp, url_prefix='/api')
    app.register_blueprint(adjuntos_bp, url_prefix='/api')
    app.register_blueprint(columnas_bp, url_prefix='/api')
    app.register_blueprint(invitaciones_bp, url_prefix='/api')  
    app.register_blueprint(boards_bp, url_prefix='/api')

    @app.route('/swagger')
    def swagger_ui():
        return redirect('/apidocs')

    @app.route('/check_jwt_config')
    def check_jwt_config():
        return {
            'JWT_SECRET_KEY': app.config.get('JWT_SECRET_KEY'),
            'JWT_TOKEN_LOCATION': app.config.get('JWT_TOKEN_LOCATION'),
            'JWT_HEADER_NAME': app.config.get('JWT_HEADER_NAME'),
            'JWT_HEADER_TYPE': app.config.get('JWT_HEADER_TYPE')
        }

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app)
