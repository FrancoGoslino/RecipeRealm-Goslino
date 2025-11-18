from base_datos.conexion import Conexion
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def crear_usuario_ejemplo():
    with Conexion("base_datos/recetas.db") as db:
        usuario_existente = db.obtener_usuario_por_email("chef@ejemplo.com")
        if usuario_existente:
            print("El usuario de ejemplo ya existe")
            return usuario_existente
        
        print("Creando usuario de ejemplo...")
        hashed_password = generate_password_hash("password123")
        db.cursor.execute(
            "INSERT INTO usuario (nombre, apellido, email, password) VALUES (?, ?, ?, ?)",
            ("Chef", "Ejemplo", "chef@ejemplo.com", hashed_password)
        )
        db.conexion.commit()
        
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
        {
            "titulo": "Pasta con Salsa Alfredo",
            "descripcion": "Un plato cremoso y reconfortante, perfecto para una cena rápida.",
            "ingredientes": "200g de fettuccine\n1 taza de crema de leche\n50g de manteca\n70g de queso parmesano rallado\n1 diente de ajo picado\nSal y pimienta al gusto",
            "instrucciones": "1. Cocinar la pasta según las instrucciones del paquete.\n2. En una sartén, derretir la manteca y saltear el ajo.\n3. Agregar la crema y el parmesano, cocinar hasta espesar.\n4. Mezclar la pasta con la salsa y servir caliente.",
            "tiempo_preparacion": 25,
            "porciones": 2,
            "imagen_url": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "etiquetas": ["Vegetariano"]
        },
        {
            "titulo": "Tacos de Carne",
            "descripcion": "Tacos mexicanos tradicionales con carne sazonada y vegetales frescos.",
            "ingredientes": "300g de carne picada\n1 cebolla\n1 tomate\n1 cucharada de condimento para tacos\n6 tortillas de maíz\nLechuga picada\nSal al gusto",
            "instrucciones": "1. Cocinar la carne con el condimento y sal.\n2. Picar la cebolla, lechuga y tomate.\n3. Calentar las tortillas.\n4. Armar los tacos con carne y vegetales.",
            "tiempo_preparacion": 15,
            "porciones": 3,
            "imagen_url": "https://images.unsplash.com/photo-1601924928376-3c31c2a3f7d0?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "etiquetas": ["Picante", "Rápido"]
        },
        {
            "titulo": "Smoothie de Frutos Rojos",
            "descripcion": "Una bebida refrescante, ideal para el desayuno o después de entrenar.",
            "ingredientes": "1 taza de frutillas\n1/2 taza de arándanos\n1 banana\n1 taza de leche o bebida vegetal\n1 cucharada de miel",
            "instrucciones": "1. Lavar los frutos rojos.\n2. Colocar todos los ingredientes en una licuadora.\n3. Procesar hasta obtener una mezcla homogénea.\n4. Servir frío.",
            "tiempo_preparacion": 5,
            "porciones": 1,
            "imagen_url": "https://images.unsplash.com/photo-1572441710534-680f39b3cd31?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "etiquetas": ["Vegano", "Saludable", "Sin TACC"]
        },
        {
            "titulo": "Pollo al Curry con Arroz",
            "descripcion": "Un plato aromático y especiado, inspirado en la cocina asiática.",
            "ingredientes": "300g de pechuga de pollo\n1 cebolla\n1 lata de leche de coco\n1 cucharada de curry en polvo\n1 taza de arroz blanco\nAceite, sal y pimienta",
            "instrucciones": "1. Cocinar el arroz.\n2. Saltear la cebolla en aceite.\n3. Agregar el pollo en cubos y cocinar.\n4. Incorporar el curry y la leche de coco.\n5. Cocinar a fuego lento 10 minutos y servir sobre arroz.",
            "tiempo_preparacion": 30,
            "porciones": 2,
            "imagen_url": "https://images.unsplash.com/photo-1625246333195-78fbf3cfa667?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "etiquetas": ["Alto en Proteínas", "Sin TACC"]
        }
    ]

    with Conexion("base_datos/recetas.db") as db:
        for receta in recetas:
            try:
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

                for etiqueta_nombre in receta.get("etiquetas", []):
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