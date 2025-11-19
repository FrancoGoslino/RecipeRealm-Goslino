# RecipeRealm

Aplicación web desarrollada con **Flask** que permite a los usuarios registrarse, iniciar sesión y gestionar recetas de cocina. Incluye sistema de comentarios, votos (likes/dislikes), etiquetas (por ejemplo: Sin TACC, Vegano, Vegetariano, etc.), y una landing page con recetas populares.

---

## Características principales

- **Autenticación de usuarios**
  - Registro de usuarios con nombre, apellido, email y contraseña.
  - Inicio y cierre de sesión con manejo de sesión vía `Flask`.
  - Protección de rutas sensibles mediante decorador `login_required`.

- **Gestión de recetas**
  - Creación de recetas por parte de usuarios registrados.
  - Campos: título, descripción, ingredientes, instrucciones, tiempo de preparación, porciones e imagen.
  - Listado de recetas con filtros por texto y etiquetas.
  - Visualización detallada de una receta con autor, comentarios, votos y recetas relacionadas.

- **Interacción social**
  - Sistema de comentarios por receta.
  - Sistema de votos (like/dislike) por usuario y por receta.
  - Cálculo de estadísticas de votos y visualización en la vista de detalle.

- **Etiquetas y filtros**
  - Etiquetas como "Sin TACC", "Vegetariano", "Vegano", "Sin Lactosa", etc.
  - Filtro de recetas por etiqueta y búsqueda por texto.

- **Datos de ejemplo**
  - Script `agregar_recetas_ejemplo.py` para poblar la base de datos con recetas, usuario y etiquetas de ejemplo.

- **Pruebas**
  - Archivo `test_app.py` con pruebas unitarias básicas sobre rutas y acceso a la base de datos usando `unittest`.

---

## Tecnologías utilizadas

- **Backend**
  - Python 3
  - Flask
  - Flask-CORS
  - Werkzeug (hash de contraseñas)

- **Base de datos**
  - SQLite (`base_datos/recetas.db`)
  - Módulo propio `base_datos/conexion.py` para manejar conexiones y operaciones (crear tablas, CRUD de usuarios y recetas, etiquetas, comentarios, votos, etc.).

- **Frontend**
  - HTML5 y Jinja2 templates (`templates/`)
  - CSS personalizado (`static/estilo.css`, `static/landing.css`, `static/auth.css`)

- **Testing**
  - `unittest` estándar de Python.

> Nota: El archivo `models.py` contiene un ejemplo de modelo con SQLAlchemy pero no es utilizado por la aplicación principal actual, que trabaja directamente con la clase `Conexion`.

---

## Estructura del proyecto

```bash
P-Recipe/
├── app.py                    # Aplicación Flask principal
├── main.py                   # Script de prueba/ejemplo para creación de tablas y clase receta
├── agregar_recetas_ejemplo.py# Script para poblar la BD con recetas y usuario de ejemplo
├── models.py                 # Ejemplo de modelo con SQLAlchemy (no usado en app.py)
├── test_app.py               # Pruebas unitarias básicas de la aplicación
├── base_datos/
│   ├── conexion.py           # Clase Conexion: manejo de SQLite, creación de tablas, consultas
│   └── recetas.db            # Base de datos SQLite (se crea automáticamente si no existe)
├── static/
│   ├── estilo.css
│   ├── landing.css
│   └── auth.css
├── templates/
│   ├── base.html             # Template base
│   ├── landing.html          # Landing page con recetas populares
│   ├── crear_cuenta.html     # Formulario de registro
│   ├── inicio_sesion.html    # Formulario de login
│   ├── perfil.html           # Perfil de usuario
│   ├── recetas.html          # Listado y búsqueda de recetas
│   ├── ver_receta.html       # Vista detallada de receta
│   ├── resultado.html        # Vista de resultados genéricos
│   └── crear_receta.html     # Formulario para crear nueva receta
└── .venv/                    # Entorno virtual (opcional, no subir a producción)
```

---

## Requisitos previos

- **Python** 3.8+ (recomendado)
- Entorno virtual de Python (opcional pero recomendado).
- SQLite (incluido por defecto en la mayoría de instalaciones de Python).

Paquetes de Python mínimos (pueden instalarse con `pip`):

- `flask`
- `flask-cors`
- `werkzeug`

Si se usa `models.py` o se planea integrar SQLAlchemy completamente:

- `flask_sqlalchemy`

> Si tu proyecto tiene un `requirements.txt`, puedes instalar todo con:
>
> ```bash
> pip install -r requirements.txt
> ```

---

## Instalación y configuración

1. **Clonar el repositorio**

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd P-Recipe
   ```

2. **(Opcional) Crear y activar entorno virtual**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/MacOS
   source .venv/bin/activate
   ```

3. **Instalar dependencias**

   ```bash
   pip install flask flask-cors werkzeug flask_sqlalchemy
   ```

   Ajusta esta lista según el archivo `requirements.txt` si existe.

4. **Configuración de la base de datos**

   La aplicación crea el archivo `base_datos/recetas.db` automáticamente al iniciar si no existe, invocando `crear_todas_las_tablas()` desde `Conexion` y generando un usuario administrador por defecto:

   - Email: `admin@example.com`
   - Password: `admin123`

   También puedes usar los scripts de apoyo:

   - `main.py`: crea tablas y un usuario de prueba.
   - `agregar_recetas_ejemplo.py`: crea tablas (si no existen), agrega etiquetas estándar y recetas de ejemplo.

   Para ejecutar el script de datos de ejemplo:

   ```bash
   python agregar_recetas_ejemplo.py
   ```

---

## Ejecución de la aplicación

Desde la carpeta del proyecto, con el entorno virtual activado (si lo usas):

```bash
python app.py
```

Por defecto, Flask se ejecutará en modo debug en:

- `http://127.0.0.1:5000/`

### Rutas principales

- `/`  
  Landing page, muestra las últimas recetas populares.

- `/crear-cuenta`  
  Formulario de registro de usuarios (GET) y procesamiento del alta (POST).

- `/iniciar-sesion`  
  Formulario de login (GET) y validación de credenciales (POST).

- `/perfil`  
  Vista de perfil del usuario autenticado.

- `/cerrar-sesion`  
  Cierra la sesión del usuario actual.

- `/recetas`  
  Listado de recetas con filtros por búsqueda y etiqueta.

- `/receta/<int:id_receta>`  
  Vista detallada de una receta, con comentarios, estadísticas de votos y recetas relacionadas.

- `/receta/<int:id_receta>/comentar` (POST)  
  Agrega un comentario a la receta. Requiere estar logueado.

- `/api/receta/<int:id_receta>/votar` (POST, JSON)  
  Endpoint para votar (like/dislike) una receta vía `fetch`/AJAX. Requiere estar logueado.

- `/crear-receta` (GET/POST)  
  Formulario para crear una nueva receta. Requiere estar logueado.

---

## Uso de la aplicación (flujo básico)

1. **Registrarse**
   - Ir a `/crear-cuenta`.
   - Completar nombre, apellido, email y contraseña.
   - Confirmar contraseña y enviar el formulario.

2. **Iniciar sesión**
   - Ir a `/iniciar-sesion`.
   - Ingresar email y contraseña registrados.

3. **Explorar recetas**
   - Ir a `/` o `/recetas`.
   - Filtrar por texto y etiquetas.
   - Hacer clic en una receta para ver el detalle.

4. **Comentar y votar** (requiere login)
   - En la vista de detalle `/receta/<id>`, agregar comentarios.
   - Usar los botones de like/dislike para votar.

5. **Crear nuevas recetas**
   - Ir a `/crear-receta`.
   - Completar los campos obligatorios y etiquetas.
   - Guardar; la app redirige al detalle de la nueva receta.

---

## Pruebas

El proyecto incluye pruebas básicas en `test_app.py` usando `unittest`.

Para ejecutar las pruebas:

```bash
python -m unittest test_app.py
```

Las pruebas cubren, entre otros:

- Carga de la landing page (`/`).
- Acceso a `/recetas`.
- Acceso a `/crear-cuenta` (GET).
- Flujo básico de registro de usuario (POST).
- Obtención de recetas desde la base de datos.
- Creación de una receta simulando usuario autenticado.

---

## Scripts adicionales

- **`main.py`**  
  Crea tablas usando `Conexion` y prueba la creación de un usuario. También incluye una clase `receta` de ejemplo para uso por consola.

- **`agregar_recetas_ejemplo.py`**  
  - Crea tablas si no existen.
  - Crea un usuario de ejemplo (`chef@ejemplo.com`).
  - Inserta etiquetas estándar.
  - Agrega varias recetas de ejemplo con sus etiquetas.

---

## Notas y posibles mejoras

- Integrar completamente SQLAlchemy usando `models.py` para reemplazar parte de la lógica directa sobre SQLite.
- Externalizar la `secret_key` de Flask a variables de entorno o archivo de configuración.
- Añadir más pruebas (por ejemplo, para comentarios, votos y filtros por etiqueta).
- Agregar paginación en el listado de recetas.
- Añadir validaciones de formularios del lado del cliente (JavaScript) y servidor más exhaustivas.

---

## Licencia

Por definir
