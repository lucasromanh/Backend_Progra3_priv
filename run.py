from app import create_app, socketio, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Usamos un contexto de conexión para ejecutar una consulta de prueba
        with db.engine.connect() as connection:
            connection.execute(text('SELECT 1'))
        print("Conexión a la base de datos exitosa")
    except Exception as e:
        print(f"Error de conexión a la base de datos: {e}")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
