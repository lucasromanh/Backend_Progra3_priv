import unittest
from flask_socketio import SocketIOTestClient
from app import create_app, db, socketio
from app.models import Usuario
from werkzeug.security import generate_password_hash

class SocketIOTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.socketio = socketio.test_client(self.app, flask_test_client=self.client)

        with self.app.app_context():
            db.create_all()
            user = Usuario(
                Nombre='Test',
                Apellido='User',
                CorreoElectronico='test@example.com',
                PasswordHash=generate_password_hash('password')  # Cambia la contraseña en producción
            )
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_socketio_connection(self):
        @self.socketio.on('connect')
        def handle_connect():
            pass  # La conexión de prueba debe ser manejada aquí

        self.socketio.connect('/')
        self.assertTrue(self.socketio.is_connected())

    def test_new_task_event(self):
        @self.socketio.on('new_task')
        def handle_new_task(data):
            self.assertIn('task', data)  # Verifica que el evento de nueva tarea contenga la clave 'task'
        
        self.socketio.connect('/')
        response = self.client.post('/api/tareas', json={
            'ProyectoID': 1,
            'Titulo': 'Test Task'
        })
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()
