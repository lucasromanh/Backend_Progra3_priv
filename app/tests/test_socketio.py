import unittest
from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

class AuthTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            user = Usuario(
                Nombre='Test',
                Apellido='User',
                CorreoElectronico='test@example.com',
                PasswordHash=generate_password_hash('Thepassword')
            )
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_login(self):
        response = self.client.post('/api/auth/login', json={
            'CorreoElectronico': 'test@example.com',
            'Password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.get_json())

if __name__ == '__main__':
    unittest.main()
