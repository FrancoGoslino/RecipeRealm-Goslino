from base_datos.conexion import Conexion
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def crear_usuario_ejemplo():
    with Conexion("base_datos/recetas.db") as db:
        # Verificar si el usuario ya existe
        usuario_existente = db.obtener_usuario_por_email("chef@ejemplo.com")
        if usuario_existente:
            print("El usuario de ejemplo ya existe")
            return usuario_existente
        
        # Si no existe, crearlo
        print("Creando usuario de ejemplo...")
        hashed_password = generate_password_hash("password123")
        db.cursor.execute(
            "INSERT INTO usuario (nombre, apellido, email, password) VALUES (?, ?, ?, ?)",
            ("Chef", "Ejemplo", "chef@ejemplo.com", hashed_password)
        )
        db.conexion.commit()
        
        # Obtener el ID del usuario recién creado
        return db.obtener_usuario_por_email("chef@ejemplo.com")

def agregar_etiquetas():
    etiquetas = [
        "Sin TACC", "Vegetariano", "Vegano", "Sin Lactosa", "Sin Huevo",
        "Apto Diabéticos", "Bajo en Sodio", "Sin Azúcar", "Keto", "Alto en Proteínas"
    ]
    
    with Conexion("base_datos/recetas.db") as db:
        for etiqueta in etiquetas:
            try:
                db.cursor.execute(
                    "INSERT OR IGNORE INTO etiquetas (nombre) VALUES (?)",
                    (etiqueta,)
                )
                db.conexion.commit()
            except Exception as e:
                print(f"Error al agregar etiqueta {etiqueta}: {e}")

def agregar_recetas_ejemplo(usuario_id):
    recetas = [
        {
            "titulo": "Ensalada César Clásica",
            "descripcion": "Una ensalada fresca y deliciosa con pollo a la parrilla y aderezo César casero.",
            "ingredientes": "1 lechuga romana\n1 pechuga de pollo\n50g de queso parmesano\n1 taza de crutones\n2 cucharadas de jugo de limón\n1 diente de ajo\n1 cucharadita de mostaza\n1/2 taza de aceite de oliva\nSal y pimienta al gusto",
            "instrucciones": "1. Cocinar el pollo a la parrilla y cortar en tiras.\n2. Lavar y cortar la lechuga.\n3. Mezclar el jugo de limón, ajo, mostaza y aceite para el aderezo.\n4. Mezclar todos los ingredientes y espolvorear con queso parmesano.",
            "tiempo_preparacion": 20,
            "porciones": 2,
            "imagen_url": "https://images.unsplash.com/photo-1546793665-c74683f339c1?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "etiquetas": ["Sin TACC", "Alto en Proteínas"]
        },
        # Agrega más recetas aquí...
    ]

    with Conexion("base_datos/recetas.db") as db:
        for receta in recetas:
            try:
                # Insertar receta
                db.cursor.execute("""
                    INSERT INTO recetas (
                        titulo, descripcion, ingredientes, instrucciones,
                        tiempo_preparacion, porciones, imagen_url, id_usuario
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    receta["titulo"],
                    receta["descripcion"],
                    receta["ingredientes"],
                    receta["instrucciones"],
                    receta["tiempo_preparacion"],
                    receta["porciones"],
                    receta.get("imagen_url", ""),
                    usuario_id
                ))
                receta_id = db.cursor.lastrowid

                # Asignar etiquetas
                for etiqueta_nombre in receta.get("etiquetas", []):
                    # Obtener o crear la etiqueta
                    db.cursor.execute(
                        "SELECT id_etiqueta FROM etiquetas WHERE nombre = ?",
                        (etiqueta_nombre,)
                    )
                    etiqueta = db.cursor.fetchone()
                    
                    if not etiqueta:
                        db.cursor.execute(
                            "INSERT INTO etiquetas (nombre) VALUES (?)",
                            (etiqueta_nombre,)
                        )
                        etiqueta_id = db.cursor.lastrowid
                    else:
                        etiqueta_id = etiqueta[0]
                    
                    # Asociar etiqueta a la receta
                    db.cursor.execute(
                        "INSERT OR IGNORE INTO receta_etiqueta (id_receta, id_etiqueta) VALUES (?, ?)",
                        (receta_id, etiqueta_id)
                    )
                
                db.conexion.commit()
                print(f"Receta agregada: {receta['titulo']}")
                
            except Exception as e:
                print(f"Error al agregar receta {receta.get('titulo')}: {e}")
                db.conexion.rollback()

if __name__ == "__main__":
    print("Creando tablas en orden correcto...")
    with Conexion("base_datos/recetas.db") as db:
        # Asegurarse de que las tablas existan
        if hasattr(db, 'crear_todas_las_tablas'):
            db.crear_todas_las_tablas()
            print("Todas las tablas fueron creadas correctamente.")
        else:
            print("Error: El método crear_todas_las_tablas no está definido")
    
    # Agregar etiquetas
    agregar_etiquetas()
    
    # Crear usuario de ejemplo y agregar recetas
    usuario = crear_usuario_ejemplo()
    if usuario:
        print(f"Usuario creado con ID: {usuario['id_usuario']}")
        agregar_recetas_ejemplo(usuario['id_usuario'])
        print("¡Recetas de ejemplo agregadas exitosamente!")
    else:
        print("Error al crear el usuario de ejemplo")