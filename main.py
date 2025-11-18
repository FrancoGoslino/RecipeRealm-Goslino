<<<<<<< HEAD
from base_datos.conexion import Conexion

# Crear una instancia de la conexión
with Conexion("base_datos/recetas.db") as db:
    # Crear todas las tablas
    db.crear_todas_las_tablas()
    
    # Probar la creación de un usuario
    usuario_id = db.crear_usuario(
        nombre="Test",
        apellido="User",
        email="test@example.com",
        password="test123"
    )
    
    if usuario_id:
        print(f"Usuario creado exitosamente con ID: {usuario_id}")
    else:
        print("Error al crear el usuario")
=======
class receta:
    def __init__(self, nombre, ingredientes, instrucciones):
        self.nombre = nombre
        self.ingredientes = ingredientes
        self.instrucciones = instrucciones

    def mostrar_receta(self):
        print(f"Receta: {self.nombre}")
        print("Ingredientes:")
        for ingrediente in self.ingredientes:
            print(f"- {ingrediente}")
        print("Instrucciones:")
        for paso in self.instrucciones:
            print(f"- {paso}")
            
            
# Ejemplo de uso
mostrar_receta: receta = receta(
    "Pasta al Pesto", 
    ["200g de pasta", "100g de albahaca fresca", "50g de piñones", "2 dientes de ajo", "50g de queso parmesano", "100ml de aceite de oliva", "Sal y pimienta al gusto"], 
    ["Cocinar la pasta según las instrucciones del paquete.", 
     "En un procesador de alimentos, mezclar la albahaca, piñones, ajo y queso parmesano.", 
     "Agregar el aceite de oliva lentamente hasta obtener una salsa suave.", 
     "Mezclar la salsa con la pasta cocida.", 
     "Sazonar con sal y pimienta al gusto."]
)

mostrar_receta.mostrar_receta()
>>>>>>> d1e0621a3fc4cb6d6d9518b5955b704353e98ee7
