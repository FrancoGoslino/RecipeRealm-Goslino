import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Conexion:
    """
    Clase para manejar la conexión a la base de datos y operaciones relacionadas.
    """
    def __init__(self, nombre_bd="base_datos/recetas.db"):
        self.conexion = sqlite3.connect(nombre_bd)
        # Configurar el row_factory para devolver diccionarios
        self.conexion.row_factory = sqlite3.Row
        self.cursor = self.conexion.cursor()
        # Habilitar el soporte de claves foráneas
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.conexion.commit()

    # -------------------------------------------------------------
    # TABLAS BASE SIN FOREIGN KEYS
    # -------------------------------------------------------------

    def crear_tabla_receta(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS recetas (
                id_receta INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo VARCHAR(100) NOT NULL,
                descripcion TEXT,
                ingredientes TEXT,
                instrucciones TEXT,
                tiempo_preparacion INTEGER,
                porciones INTEGER,
                imagen_url TEXT,
                id_usuario INTEGER,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT 1,
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
            )
        """)
        self.conexion.commit()
    
    def crear_tabla_restriccion(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS restriccion (
                id_restriccion INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(255)
            )
        """)
        self.conexion.commit()

    def crear_tabla_categoria(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categoria (
                id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(255)
            )
        """)
        self.conexion.commit()

    def crear_tabla_usuario(self):
        """Crea la tabla de usuarios si no existe."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuario (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(255) NOT NULL,
                    apellido VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT 1
                )
            """)
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"Error al crear tabla usuario: {e}")
            return False

    def crear_tabla_votacion(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS votacion (
                id_votacion INTEGER PRIMARY KEY AUTOINCREMENT,
                votado_positivo BOOLEAN,
                votado_negativo BOOLEAN
            )
        """)
        self.conexion.commit()
    
    def obtener_comentarios_receta(self, id_receta):
        """Obtiene todos los comentarios de una receta"""
        self.cursor.execute("""
            SELECT c.*, u.nombre as nombre_usuario
            FROM comentarios c
            JOIN usuario u ON c.id_usuario = u.id_usuario
            WHERE c.id_receta = ?
            ORDER BY c.fecha_creacion DESC
        """, (id_receta,))
        
        comentarios = []
        for row in self.cursor.fetchall():
            comentario = dict(row)
            # Convert the string date to a datetime object
            if 'fecha_creacion' in comentario and isinstance(comentario['fecha_creacion'], str):
                from datetime import datetime
                try:
                    # Try ISO format first (for example recipes)
                    if 'T' in comentario['fecha_creacion']:
                        comentario['fecha_creacion'] = datetime.fromisoformat(comentario['fecha_creacion'])
                    else:
                        # Try SQLite datetime format
                        comentario['fecha_creacion'] = datetime.strptime(
                            comentario['fecha_creacion'], 
                            '%Y-%m-%d %H:%M:%S'
                        )
                except (ValueError, TypeError) as e:
                    print(f"Error al convertir fecha: {e}")
                    # If conversion fails, keep the original string
                    pass
            comentarios.append(comentario)
        return comentarios
    
    def crear_tabla_empleado(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS empleado (
                id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(255),
                apellido VARCHAR(255),
                email VARCHAR(255) UNIQUE,
                fecha_ingreso DATETIME,
                permisos VARCHAR(255),
                activo BOOLEAN
            )
        """)
        self.conexion.commit()

    def crear_tabla_permisos(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS permisos (
                id_permisos INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(255)
            )
        """)
        self.conexion.commit()

    def crear_tabla_ingrediente(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingrediente (
                id_ingrediente INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(255)
            )
        """)
        self.conexion.commit()

    def crear_tabla_lista_favoritos(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS lista_favoritos (
                id_lista_favorito INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                nombre VARCHAR(255),
                descripcion VARCHAR(255),
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
            )
        """)
        self.conexion.commit()

    # -------------------------------------------------------------
    # TABLAS PUENTE (RELACIONES MANY TO MANY)
    # -------------------------------------------------------------

    def crear_tabla_comentarios(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS comentarios (
                id_comentario INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT NOT NULL,
                id_usuario INTEGER NOT NULL,
                id_receta INTEGER NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
                FOREIGN KEY (id_receta) REFERENCES recetas(id_receta) ON DELETE CASCADE
            )
        """)
        self.conexion.commit()
    
    def crear_tabla_receta_has_ingrediente(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS receta_has_ingrediente (
                id_receta_ingrediente INTEGER PRIMARY KEY AUTOINCREMENT,
                id_receta INTEGER,
                id_ingrediente INTEGER,
                cantidad FLOAT,
                FOREIGN KEY (id_receta) REFERENCES receta(id_receta),
                FOREIGN KEY (id_ingrediente) REFERENCES ingrediente(id_ingrediente)
            )
        """)
        self.conexion.commit()

    def crear_tabla_receta_has_restriccion(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS receta_has_restriccion (
                id_receta_restriccion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_receta INTEGER,
                id_restriccion INTEGER,
                FOREIGN KEY (id_receta) REFERENCES recetas(id_receta) ON DELETE CASCADE,
                FOREIGN KEY (id_restriccion) REFERENCES restriccion(id_restriccion)
            )
        """)
        self.conexion.commit()

    def crear_tabla_receta_has_categoria(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS receta_has_categoria (
                id_receta_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
                id_categoria INTEGER,
                id_receta INTEGER,
                FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria),
                FOREIGN KEY (id_receta) REFERENCES recetas(id_receta) ON DELETE CASCADE
            )
        """)
        self.conexion.commit()

    def crear_tabla_empleado_has_permisos(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS empleado_has_permisos (
                id_empleado_permisos INTEGER PRIMARY KEY AUTOINCREMENT,
                id_permisos INTEGER,
                id_empleado INTEGER,
                fecha_otorga DATETIME,
                FOREIGN KEY (id_permisos) REFERENCES permisos(id_permisos),
                FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado)
            )
        """)
        self.conexion.commit()

    def crear_tabla_usuario_has_permisos(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuario_has_permisos (
                id_usuario_permisos INTEGER PRIMARY KEY AUTOINCREMENT,
                id_permisos INTEGER,
                id_usuario INTEGER,
                fecha_otorga DATETIME,
                FOREIGN KEY (id_permisos) REFERENCES permisos(id_permisos),
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
            )
        """)
        self.conexion.commit()

    def crear_tabla_lista_favoritos_has_receta(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS lista_favoritos_has_receta (
                id_lista_favorito INTEGER,
                id_receta INTEGER,
                fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id_lista_favorito, id_receta),
                FOREIGN KEY (id_lista_favorito) REFERENCES lista_favoritos(id_lista_favorito) ON DELETE CASCADE,
                FOREIGN KEY (id_receta) REFERENCES recetas(id_receta) ON DELETE CASCADE
            )
        """)
        self.conexion.commit()
    
    def crear_todas_las_tablas(self):
        """Crea todas las tablas en el orden correcto para evitar conflictos de claves foráneas"""
        try:
            # 1. Primero las tablas sin dependencias
            self.crear_tabla_permisos()
            self.crear_tabla_restriccion()
            self.crear_tabla_categoria()
            self.crear_tabla_usuario()
            self.crear_tabla_empleado()
            self.crear_tabla_ingrediente()
            self.crear_tabla_etiquetas()  # Asegurarse de que las etiquetas se creen antes de recetas
            
            # 2. Luego las tablas que dependen de las anteriores
            self.crear_tabla_receta()  # Depende de usuario
            self.crear_tabla_comentarios()  # Depende de usuario y receta
            self.crear_tabla_votos()  # Depende de usuario y receta
            self.crear_tabla_lista_favoritos()  # Depende de usuario
            
            # 3. Tablas de relación many-to-many
            self.crear_tabla_receta_etiqueta()  # Depende de recetas y etiquetas
            self.crear_tabla_receta_has_ingrediente()
            self.crear_tabla_receta_has_restriccion()
            self.crear_tabla_receta_has_categoria()
            self.crear_tabla_empleado_has_permisos()
            self.crear_tabla_usuario_has_permisos()
            self.crear_tabla_lista_favoritos_has_receta()
            
            print("Todas las tablas fueron creadas correctamente.")
            return True
            
        except Exception as e:
            print(f"Error al crear las tablas: {e}")
            self.conexion.rollback()
            return False
    
    # -------------------------------------------------------------
    # CREAR TODAS LAS TABLAS EN ORDEN CORRECTO SIN CONFLICTOS
    # -------------------------------------------------------------

    def crear_todas_las_tablas(self):
        """Crea todas las tablas en el orden correcto para evitar conflictos de claves foráneas"""
        try:
            # 1. Primero las tablas sin dependencias
            self.crear_tabla_permisos()
            self.crear_tabla_restriccion()
            self.crear_tabla_categoria()
            self.crear_tabla_usuario()
            self.crear_tabla_empleado()
            self.crear_tabla_ingrediente()
        
            # 2. Luego las tablas que dependen de las anteriores
            self.crear_tabla_receta()  # Depende de usuario
            self.crear_tabla_etiquetas()  # Nueva tabla para etiquetas
            self.crear_tabla_receta_etiqueta()  # Tabla puente entre recetas y etiquetas
            self.crear_tabla_comentarios()  # Depende de usuario y receta
            self.crear_tabla_votos()  # Depende de usuario y receta
            self.crear_tabla_lista_favoritos()  # Depende de usuario
        
            # 3. Finalmente las tablas de relación many-to-many
            self.crear_tabla_receta_has_ingrediente()
            self.crear_tabla_receta_has_restriccion()
            self.crear_tabla_receta_has_categoria()
            self.crear_tabla_empleado_has_permisos()
            self.crear_tabla_usuario_has_permisos()
            self.crear_tabla_lista_favoritos_has_receta()
        
            print("Todas las tablas fueron creadas correctamente.")
            return True
        
        except Exception as e:
            print(f"Error al crear las tablas: {e}")
            self.conexion.rollback()
            return False

    def crear_tabla_etiquetas(self):
        """Crea la tabla de etiquetas para las recetas"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS etiquetas (
                id_etiqueta INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL
            )
        """)
        self.conexion.commit()

    def crear_tabla_receta_etiqueta(self):
        """Crea la tabla de relación entre recetas y etiquetas"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS receta_etiqueta (
                id_receta INTEGER,
                id_etiqueta INTEGER,
                PRIMARY KEY (id_receta, id_etiqueta),
                FOREIGN KEY (id_receta) REFERENCES recetas(id_receta) ON DELETE CASCADE,
                FOREIGN KEY (id_etiqueta) REFERENCES etiquetas(id_etiqueta) ON DELETE CASCADE
            )
        """)
        self.conexion.commit()
        
    def crear_tabla_votos(self):
        """Crea la tabla de votos (likes/dislikes)"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS votos ( 
                id_receta INTEGER,
                id_usuario INTEGER,
                tipo_voto INTEGER NOT NULL,  -- 1 para like, -1 para dislike
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id_receta, id_usuario),
                FOREIGN KEY (id_receta) REFERENCES recetas(id_receta) ON DELETE CASCADE,
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
            )
        """)
        self.conexion.commit()
    
    # ====================================================
    # MÉTODOS PARA MANEJO DE USUARIOS
    # ====================================================

    def crear_usuario(self, nombre, apellido, email, password):
        """
        Crea un nuevo usuario en la base de datos.
        
        Args:
            nombre (str): Nombre del usuario
            apellido (str): Apellido del usuario
            email (str): Email del usuario (debe ser único)
            password (str): Contraseña en texto plano (se hasheará automáticamente)
            
        Returns:
            int or None: ID del usuario creado o None si hubo un error
        """
        try:
            print(f"Intentando crear usuario: {email}")  # Depuración
            hashed_password = generate_password_hash(password)
            print(f"Contraseña hasheada correctamente")  # Depuración
            
            self.cursor.execute(
                """
                INSERT INTO usuario (nombre, apellido, email, password)
                VALUES (?, ?, ?, ?)
                """,
                (nombre, apellido, email, hashed_password)
            )
            self.conexion.commit()
            user_id = self.cursor.lastrowid
            print(f"Usuario creado con ID: {user_id}")  # Depuración
            return user_id
        
        except sqlite3.IntegrityError as e:
            print(f"Error de integridad al crear usuario: {e}")  # Depuración
            if "UNIQUE constraint failed" in str(e):
                print("El correo electrónico ya está registrado")
            hashed_password = generate_password_hash(password)
            self.cursor.execute(
                """
                INSERT INTO usuario (nombre, apellido, email, password)
                VALUES (?, ?, ?, ?)
                """,
                (nombre, apellido, email, hashed_password)
            )
            self.conexion.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                print("Error: El correo electrónico ya está registrado")
            else:
                print(f"Error de base de datos al crear usuario: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al crear usuario: {e}")
            return None

    def verificar_usuario(self, email, password):
        """
        Verifica las credenciales de un usuario.
        
        Args:
            email (str): Email del usuario
            password (str): Contraseña en texto plano
            
        Returns:
            dict or None: Diccionario con los datos del usuario si las credenciales son correctas,
                        None en caso contrario
        """
        try:
            self.cursor.execute(
                """
                SELECT id_usuario, nombre, apellido, email, password 
                FROM usuario 
                WHERE email = ? AND activo = 1
                """,
                (email,)
            )
            usuario = self.cursor.fetchone()
            
            if usuario and check_password_hash(usuario[4], password):
                return {
                    'id': usuario[0],
                    'nombre': usuario[1],
                    'apellido': usuario[2],
                    'email': usuario[3]
                }
            return None
        except Exception as e:
            print(f"Error al verificar usuario: {e}")
            return None

    def obtener_usuario_por_id(self, id_usuario):
        """
        Obtiene un usuario por su ID.
        
        Args:
            id_usuario (int): ID del usuario a buscar
            
        Returns:
            tuple or None: Tupla con los datos del usuario o None si no se encuentra
        """
        try:
            self.cursor.execute(
                """
                SELECT id_usuario, nombre, apellido, email, fecha_registro, activo
                FROM usuario 
                WHERE id_usuario = ?
                """,
                (id_usuario,)
            )
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener usuario por ID: {e}")
            return None
            
    def existe_email(self, email):
        """
        Verifica si un email ya está registrado en la base de datos.
        
        Args:
            email (str): Email a verificar
            
        Returns:
            bool: True si el email existe, False en caso contrario
        """
        try:
            self.cursor.execute(
                "SELECT 1 FROM usuario WHERE email = ?",
                (email,)
            )
            return self.cursor.fetchone() is not None
        except Exception as e:
            print(f"Error al verificar email: {e}")
            return False

    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos."""
        try:
            if self.conexion:
                self.cursor.close()
                self.conexion.close()
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")
    
    def __enter__(self):
        """Permite usar la clase con el patrón 'with'."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Asegura que la conexión se cierre al salir del bloque 'with'."""
        self.cerrar_conexion()

    def obtener_recetas(self, busqueda=None, etiqueta=None, limite=10, offset=0):
        query = """
            SELECT r.*, u.nombre as autor 
        FROM recetas r
        JOIN usuario u ON r.id_usuario = u.id_usuario
        WHERE 1=1
        """
        params = []
        
        if busqueda:
            query += " AND (r.titulo LIKE ? OR r.descripcion LIKE ? OR r.ingredientes LIKE ?)"
            params.extend([f'%{busqueda}%'] * 3)
        
        if etiqueta:
            query += """
                AND r.id_receta IN (
                    SELECT re.id_receta 
                    FROM receta_etiqueta re
                    JOIN etiquetas e ON re.id_etiqueta = e.id_etiqueta
                    WHERE e.nombre = ?
                )
            """
            params.append(etiqueta)
        
        query += " ORDER BY r.fecha_creacion DESC LIMIT ? OFFSET ?"
        params.extend([limite, offset])
        
        self.cursor.execute(query, params)
        recetas = [dict(row) for row in self.cursor.fetchall()]
        
        # Agregar etiquetas a cada receta
        for receta in recetas:
            receta['etiquetas'] = self.obtener_etiquetas_receta(receta['id_receta'])
        
        return recetas

    def obtener_receta_por_id(self, id_receta):
        """
        Obtiene una receta por su ID con toda su información.
        
        Args:
            id_receta (int): ID de la receta a buscar
            
        Returns:
            dict or None: Diccionario con los datos de la receta o None si no se encuentra
        """
        try:
            self.cursor.execute("""
                SELECT r.*, u.nombre || ' ' || u.apellido as autor 
                FROM recetas r
                JOIN usuario u ON r.id_usuario = u.id_usuario
                WHERE r.id_receta = ?
            """, (id_receta,))
            
            receta = self.cursor.fetchone()
            if not receta:
                return None
                
            # Convertir a diccionario
            receta_dict = dict(receta)
            
            # Obtener etiquetas de la receta
            receta_dict['etiquetas'] = self.obtener_etiquetas_receta(id_receta)
            
            # Asegurar que los campos estén presentes
            receta_dict.setdefault('ingredientes', '')
            receta_dict.setdefault('instrucciones', '')
            receta_dict.setdefault('tiempo_preparacion', 0)
            receta_dict.setdefault('porciones', 1)
            receta_dict.setdefault('imagen_url', '')
            
            return receta_dict
            
        except Exception as e:
            print(f"Error al obtener receta por ID: {e}")
            return None

    def obtener_etiquetas_receta(self, id_receta):
        self.cursor.execute("""
            SELECT e.* 
            FROM etiquetas e
            JOIN receta_etiqueta re ON e.id_etiqueta = re.id_etiqueta
            WHERE re.id_receta = ?
        """, (id_receta,))
        return [dict(row) for row in self.cursor.fetchall()]

    def obtener_todas_etiquetas(self):
        self.cursor.execute("SELECT * FROM etiquetas")
        return [dict(row) for row in self.cursor.fetchall()]

    def agregar_comentario(self, id_receta, id_usuario, contenido):
        self.cursor.execute("""
            INSERT INTO comentarios (id_receta, id_usuario, descripcion)
            VALUES (?, ?, ?)
        """, (id_receta, id_usuario, contenido))
        self.conexion.commit()
        return self.cursor.lastrowid

    def obtener_comentarios_receta(self, id_receta):
        self.cursor.execute("""
            SELECT c.*, u.nombre, u.apellido 
            FROM comentarios c
            JOIN usuario u ON c.id_usuario = u.id_usuario
            WHERE c.id_receta = ?
            ORDER BY c.fecha_creacion DESC
        """, (id_receta,))
        return [dict(row) for row in self.cursor.fetchall()]

    def votar_receta(self, id_receta, id_usuario, tipo_voto):
        # Verificar si ya existe un voto
        self.cursor.execute("""
            SELECT id FROM votos 
            WHERE id_receta = ? AND id_usuario = ?
        """, (id_receta, id_usuario))
        
        if self.cursor.fetchone():
            # Actualizar voto existente
            self.cursor.execute("""
                UPDATE votos 
                SET tipo_voto = ?
                WHERE id_receta = ? AND id_usuario = ?
            """, (tipo_voto, id_receta, id_usuario))
        else:
            # Insertar nuevo voto
            self.cursor.execute("""
                INSERT INTO votos (id_receta, id_usuario, tipo_voto)
                VALUES (?, ?, ?)
            """, (id_receta, id_usuario, tipo_voto))
        
        self.conexion.commit()
        return self.obtener_estadisticas_votos(id_receta)

    def obtener_estadisticas_votos(self, id_receta):
        self.cursor.execute("""
            SELECT 
                SUM(CASE WHEN tipo_voto = 1 THEN 1 ELSE 0 END) as likes,
                SUM(CASE WHEN tipo_voto = -1 THEN 1 ELSE 0 END) as dislikes
            FROM votos
            WHERE id_receta = ?
        """, (id_receta,))
        return dict(self.cursor.fetchone() or {'likes': 0, 'dislikes': 0})

    def obtener_voto_usuario(self, id_receta, id_usuario):
        
        self.cursor.execute("""
            SELECT tipo_voto 
            FROM votos 
            WHERE id_receta = ? AND id_usuario = ?
        """, (id_receta, id_usuario))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def obtener_usuario_por_email(self, email):
        """Obtiene un usuario por su email"""
        self.cursor.execute("""
            SELECT id_usuario, nombre, apellido, email, fecha_registro, activo 
            FROM usuario 
            WHERE email = ?
        """, (email,))
        columns = [column[0] for column in self.cursor.description]
        usuario = self.cursor.fetchone()
        return dict(zip(columns, usuario)) if usuario else None

    def obtener_usuario_por_id(self, id_usuario):
        """Obtiene un usuario por su ID"""
        self.cursor.execute("SELECT * FROM usuario WHERE id_usuario = ?", (id_usuario,))
        usuario = self.cursor.fetchone()
        return dict(usuario) if usuario else None

    def obtener_ultimas_recetas(self, limite=6):
        self.cursor.execute("""
            SELECT r.*, u.nombre as autor 
            FROM recetas r
            JOIN usuario u ON r.id_usuario = u.id_usuario
            ORDER BY r.fecha_creacion DESC
            LIMIT ?
        """, (limite,))
        return [dict(row) for row in self.cursor.fetchall()]