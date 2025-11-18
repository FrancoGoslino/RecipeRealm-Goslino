from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_cors import CORS
from base_datos.conexion import Conexion
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave segura
CORS(app)

# Configuración de la base de datos
DB_NAME = "base_datos/recetas.db"

def get_db_connection():
    """Crea y devuelve una conexión a la base de datos"""
    return Conexion("base_datos/recetas.db")

# Decorador para verificar que el usuario está autenticado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('iniciar_sesion', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Ruta principal (landing page)
@app.route('/')
def index():
    return render_template('landing.html')
    

# Ruta para el formulario de registro
@app.route('/crear-cuenta', methods=['GET', 'POST'])
def crear_cuenta():
    if request.method == 'POST':
        # Get form data
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')  # Make sure this matches your form field name
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Debug print to see what we're getting
        print(f"Form data: nombre={nombre}, apellido={apellido}, email={email}")

        # Validate required fields
        if not all([nombre, apellido, email, password, confirm_password]):
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('crear_cuenta'))

        # Validate password match
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('crear_cuenta'))

        # Check if email already exists
        with get_db_connection() as db:
            if db.existe_email(email):
                flash('El correo electrónico ya está registrado', 'error')
                return redirect(url_for('crear_cuenta'))

            # Create the user
            try:
                usuario_id = db.crear_usuario(
                    nombre=nombre,
                    apellido=apellido,  # Make sure this is included
                    email=email,
                    password=password
                )

                if usuario_id:
                    flash('¡Registro exitoso! Por favor inicia sesión.', 'success')
                    return redirect(url_for('iniciar_sesion'))
                else:
                    flash('Error al crear la cuenta. Por favor, inténtalo de nuevo.', 'error')
            except Exception as e:
                print(f"Error al crear usuario: {str(e)}")
                flash('Error al crear la cuenta. Por favor, inténtalo de nuevo.', 'error')

    return render_template('crear_cuenta.html')

# Ruta para el inicio de sesión
@app.route('/iniciar-sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        with get_db_connection() as db:
            usuario = db.verificar_usuario(email, password)
            
            if usuario:
                session['user_id'] = usuario['id']
                session['nombre'] = usuario['nombre']
                session['email'] = usuario['email']
                flash(f'¡Bienvenido de nuevo, {usuario["nombre"]}!', 'success')
                return redirect(url_for('perfil'))
            else:
                flash('Correo o contraseña incorrectos', 'error')
                return redirect(url_for('iniciar_sesion'))

    return render_template('inicio_sesion.html')

# Ruta para el perfil del usuario (requiere inicio de sesión)
@app.route('/perfil')
def perfil():
    if 'user_id' not in session:
        return redirect(url_for('iniciar_sesion'))
    
    return render_template('perfil.html', usuario={
        'nombre': session.get('nombre'),
        'email': session.get('email')
    })

# Ruta para cerrar sesión
@app.route('/cerrar-sesion')
def cerrar_sesion():
    session.clear()
    return redirect(url_for('index'))

# Crear tablas si no existen al iniciar la aplicación
with app.app_context():
    if not os.path.exists(DB_NAME):
        with get_db_connection() as db:
            db.crear_todas_las_tablas()
            # Crear un usuario de prueba
            db.crear_usuario(
                nombre="Admin",
                apellido="Sistema",
                email="admin@example.com",
                password="admin123"
            )

@app.route('/recetas')
def ver_recetas():
    busqueda = request.args.get('buscar', '')
    etiqueta = request.args.get('etiqueta', '')
    
    with get_db_connection() as db:
        etiquetas = db.obtener_todas_etiquetas()
        recetas = db.obtener_recetas(busqueda=busqueda, etiqueta=etiqueta)
    
    return render_template('recetas.html', 
                         recetas=recetas, 
                         etiquetas=etiquetas,
                         busqueda_actual=busqueda,
                         etiqueta_actual=etiqueta)   

@app.route('/receta/<int:id_receta>')
def ver_receta(id_receta):
    with get_db_connection() as db:
        # Obtener receta actual
        receta = db.obtener_receta_por_id(id_receta)
        if not receta:
            flash('Receta no encontrada', 'error')
            return redirect(url_for('ver_recetas'))
            
        # Obtener comentarios
        comentarios = db.obtener_comentarios_receta(id_receta)
        
        # Obtener estadísticas de votos
        estadisticas = db.obtener_estadisticas_votos(id_receta)
        
        # Obtener voto del usuario actual
        voto_usuario = 0
        if 'user_id' in session:
            voto_usuario = db.obtener_voto_usuario(id_receta, session['user_id'])
        
        # Obtener recetas relacionadas (mismas etiquetas)
        recetas_relacionadas = []
        if receta.get('etiquetas'):
            etiqueta_ids = [e['id_etiqueta'] for e in receta['etiquetas']]
            if etiqueta_ids:
                placeholders = ','.join(['?'] * len(etiqueta_ids))
                query = f"""
                    SELECT DISTINCT r.*, u.nombre as autor 
                    FROM recetas r
                    JOIN usuario u ON r.id_usuario = u.id_usuario
                    JOIN receta_etiqueta re ON r.id_receta = re.id_receta
                    WHERE r.id_receta != ? AND re.id_etiqueta IN ({placeholders})
                    LIMIT 3
                """
                params = [id_receta] + etiqueta_ids
                db.cursor.execute(query, params)
                recetas_relacionadas = [dict(row) for row in db.cursor.fetchall()]
        
        # Si no hay suficientes recetas relacionadas, completar con las más recientes
        if len(recetas_relacionadas) < 3:
            query = """
                SELECT r.*, u.nombre as autor 
                FROM recetas r
                JOIN usuario u ON r.id_usuario = u.id_usuario
                WHERE r.id_receta != ?
                ORDER BY r.fecha_creacion DESC
                LIMIT ?
            """
            limit = 3 - len(recetas_relacionadas)
            db.cursor.execute(query, (id_receta, limit))
            additional_recipes = [dict(row) for row in db.cursor.fetchall()]
            recetas_relacionadas.extend(additional_recipes)
    
    return render_template('ver_receta.html',
                         receta=receta,
                         comentarios=comentarios,
                         estadisticas=estadisticas,
                         voto_usuario=voto_usuario,
                         recetas_relacionadas=recetas_relacionadas)

@app.route('/receta/<int:id_receta>/comentar', methods=['POST'])
@login_required
def comentar_receta(id_receta):
    contenido = request.form.get('contenido', '').strip()
    if not contenido:
        flash('El comentario no puede estar vacío', 'error')
        return redirect(url_for('ver_receta', id_receta=id_receta))
    
    with get_db_connection() as db:
        db.agregar_comentario(
            id_receta=id_receta,
            id_usuario=session['user_id'],
            contenido=contenido
        )
    
    flash('Comentario agregado correctamente', 'success')
    return redirect(url_for('ver_receta', id_receta=id_receta) + '#comentarios')

@app.route('/api/receta/<int:id_receta>/votar', methods=['POST'])
@login_required
def votar_receta(id_receta):
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        tipo_voto = int(request.json.get('tipo_voto', 0))
        if tipo_voto not in [1, -1]:
            raise ValueError("Tipo de voto no válido")
    except (ValueError, TypeError):
        return jsonify({'error': 'Tipo de voto no válido'}), 400
    
    with get_db_connection() as db:
        # Si el usuario ya votó de la misma manera, quitamos el voto
        voto_actual = db.obtener_voto_usuario(id_receta, session['user_id'])
        if voto_actual == tipo_voto:
            tipo_voto = 0  # Para eliminar el voto
        
        db.votar_receta(
            id_receta=id_receta,
            id_usuario=session['user_id'],
            tipo_voto=tipo_voto
        )
        estadisticas = db.obtener_estadisticas_votos(id_receta)
    
    return jsonify({
        'success': True,
        'likes': estadisticas['likes'],
        'dislikes': estadisticas['dislikes'],
        'mi_voto': tipo_voto if tipo_voto != 0 else 0
    })


@app.route('/crear-receta', methods=['GET', 'POST'])
@login_required
def crear_receta():
    if request.method == 'POST':
        # Get form data
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        ingredientes = request.form.get('ingredientes')
        instrucciones = request.form.get('instrucciones')
        tiempo_preparacion = request.form.get('tiempo_preparacion')
        porciones = request.form.get('porciones')
        etiquetas = request.form.getlist('etiquetas')
        
        # Validate required fields
        if not all([titulo, descripcion, ingredientes, instrucciones, tiempo_preparacion, porciones]):
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('crear_receta'))
        
        try:
            with get_db_connection() as db:
                # Insert recipe
                db.cursor.execute("""
                    INSERT INTO recetas (
                        titulo, descripcion, ingredientes, instrucciones,
                        tiempo_preparacion, porciones, id_usuario
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    titulo,
                    descripcion,
                    ingredientes,
                    instrucciones,
                    int(tiempo_preparacion),
                    int(porciones),
                    session['user_id']
                ))
                receta_id = db.cursor.lastrowid
                
                # Process tags
                if etiquetas:
                    for etiqueta_id in etiquetas:
                        db.cursor.execute("""
                            INSERT INTO receta_etiqueta (id_receta, id_etiqueta)
                            VALUES (?, ?)
                        """, (receta_id, etiqueta_id))
                
                db.conexion.commit()
                flash('¡Receta creada exitosamente!', 'success')
                return redirect(url_for('ver_receta', id_receta=receta_id))
                
        except Exception as e:
            print(f"Error al crear la receta: {e}")
            flash('Ocurrió un error al crear la receta. Por favor, inténtalo de nuevo.', 'error')
            return redirect(url_for('crear_receta'))
    
    # If it's a GET request, show the form
    with get_db_connection() as db:
        etiquetas = db.obtener_todas_etiquetas()
    
    return render_template('crear_receta.html', etiquetas=etiquetas)

if __name__ == '__main__':
    app.run(debug=True)