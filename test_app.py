import unittest
import os
import tempfile
from app import app, get_db_connection
from base_datos.conexion import Conexion

class TestRecipeApp(unittest.TestCase):
    def setUp(self):
        # Configuración para pruebas
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        
        # Crear tablas de prueba
        with app.app_context():
            with get_db_connection() as db:
                db.crear_todas_las_tablas()
    
    def tearDown(self):
        # Limpiar después de las pruebas
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_landing_page(self):
        """Prueba que la página principal cargue correctamente"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Recetas Populares', response.data)

    def test_ver_recetas(self):
        """Prueba la ruta de ver recetas"""
        response = self.app.get('/recetas')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Buscar recetas', response.data)

    def test_crear_cuenta_get(self):
        """Prueba el formulario de registro (GET)"""
        response = self.app.get('/crear-cuenta')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Crear Cuenta', response.data)

    def test_crear_cuenta_post(self):
        """Prueba el registro de un nuevo usuario (POST)"""
        response = self.app.post('/crear-cuenta', data=dict(
            nombre='Test',
            apellido='User',
            email='test@example.com',
            password='test123',
            confirmar_password='test123'
        ), follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Iniciar Sesi', response.data)  # Redirige a login

    def test_obtener_recetas(self):
        """Prueba la obtención de recetas desde la base de datos"""
        with app.app_context():
            with get_db_connection() as db:
                recetas = db.obtener_ultimas_recetas(limite=3)
                self.assertIsInstance(recetas, list)
                # Verifica que cada receta tenga los campos esperados
                if recetas:
                    self.assertIn('titulo', recetas[0])
                    self.assertIn('descripcion', recetas[0])

    def test_crear_receta(self):
        """Prueba la creación de una receta (requiere autenticación)"""
        # Ccrear un usuario de prueba
        with app.app_context():
            with get_db_connection() as db:
                db.crear_usuario(
                    nombre='Test',
                    apellido='User',
                    email='test@example.com',
                    password='test123'
                )
        
        # Iniciar sesión
        self.app.post('/iniciar-sesion', data=dict(
            email='test@example.com',
            password='test123'
        ), follow_redirects=True)
        
        # Crear una receta
        response = self.app.post('/crear-receta', data=dict(
            titulo='Receta de prueba',
            descripcion='Esta es una receta de prueba',
            ingredientes='Ingrediente 1\nIngrediente 2',
            instrucciones='Paso 1\nPaso 2',
            tiempo_preparacion=30,
            porciones=4
        ), follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Receta de prueba', response.data)

if __name__ == '__main__':
    unittest.main()