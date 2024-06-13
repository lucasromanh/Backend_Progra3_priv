from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
from flask_cors import CORS
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()

def create_app(config_class='config.DevelopmentConfig'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    CORS(app)

    Swagger(app)

    from .routes.usuarios import usuarios_bp
    from .routes.perfiles import perfiles_bp
    from .routes.tareas import tareas_bp
    from .routes.comentarios import comentarios_bp
    from .routes.notificaciones import notificaciones_bp
    from .routes.etiquetas import etiquetas_bp
    from .routes.adjuntos import adjuntos_bp

    app.register_blueprint(usuarios_bp, url_prefix='/api')
    app.register_blueprint(perfiles_bp, url_prefix='/api')
    app.register_blueprint(tareas_bp, url_prefix='/api')
    app.register_blueprint(comentarios_bp, url_prefix='/api')
    app.register_blueprint(notificaciones_bp, url_prefix='/api')
    app.register_blueprint(etiquetas_bp, url_prefix='/api')
    app.register_blueprint(adjuntos_bp, url_prefix='/api')

    @app.route('/swagger')
    def swagger_ui():
        return redirect('/apidocs')

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app)
