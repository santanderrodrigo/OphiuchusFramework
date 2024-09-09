# Framework para la materia de Proyecto Informático

Este es un framework personalizado para construir aplicaciones web en Python. A continuación, se detallan las instrucciones para usar el framework, ejecutar la aplicación y organizar el proyecto.

## Estructura del Proyecto

- `src/`
  - `app.py`: Archivo principal para ejecutar la aplicación.
  - `assets/`
    - `img/`
    - `css/`
    - `js/`
  - `core/`
    - `router.py`: Manejador de rutas y servidor HTTP.
    - `sessions_service.py`: Servicio para manejar sesiones.
  - `routes/`
    - `routes.py`: Definición de rutas.
  - `controllers/`: Controladores de la aplicación.
  - `models/`: Modelos de datos.
  - `views/`: Vistas de la aplicación.

## Instrucciones
### 1. Definir Rutas

Las rutas se definen en el archivo `routes/routes.py`. Aquí es donde se asocian las rutas con sus respectivos controladores y acciones.

register_route_with_injector(METODO, PATH, CONTROLLER NAME, CONTROLER FUNCTION,  [LISTA DE MIDDLEWARES])

Los middlewares deberán pasarse como nombre de da la clase

Ejemplo:
```python
    add_route('GET', '/', 'HomeController', 'index')
    add_route('GET', '/dashboard', 'DashboardController', 'show_dashboard', [AuthMiddleware])
    add_route('GET', '/login', 'LoginController', 'show')
    add_route('POST', '/login', 'LoginController', 'login')
    add_route('GET', '/logout', 'LoginController', 'logout')
    add_route('GET', '/about', 'HomeController', 'about')
```

### 2. Crear Controladores
Los controladores se ubican en el directorio controllers/. Cada controlador es una clase que contiene métodos que actúan como acciones para las rutas.

Ejemplo con retorno de texto:
```python
# controllers/HomeController.py
class HomeController(BaseController):
    def index(self):
        return "Bienvenido a la página principal"
```
Ejemplo con retorno de vista:
```python
# controllers/HomeController.py
class HomeController(BaseController):
    def index(self):
        return self.view("home")
```
Ejemplo con retorno de vista con contexto:
```python
# controllers/HomeController.py
class HomeController(BaseController):
    def index(self):
        # Lógica del controlador
        context = {
            "title": "Home Page",
            "header": "Welcome to the Home Page",
            "content": "This is the content of the home page."
        }
        return self.view("home", context)
```

Ejemplo con retorno de redireccion:
```python
# controllers/HomeController.py
class HomeController(BaseController):
    def index(self):
        # Lógica del controlador
        return self.redirect('/login')
```

### 3. Crear Modelos
Los modelos se ubican en el directorio models/. Aquí es donde se definen las estructuras de datos y las interacciones con la base de datos.

Ejemplo:
```python
# models/User.py
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```

### 4. Crear Vistas
Las vistas se ubican en el directorio views/. Aquí es donde se definen las plantillas HTML y la lógica de presentación.

Ejemplo:
```html
<!-- views/home.html -->
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Página Principal</title>
</head>
<body>
    <h1>Bienvenido a la página principal</h1>
    <h2> {{ VALUE }}
</body>
</html>
```

{{ VALUE }} Reemplaza el valor por el valor definido en el contexto
{{ !VALUE }} Reemplazo sin escapado de caracteres

### 5. Ejecutar la Aplicación
Para montar el servidor y ejecutar la aplicación, utiliza el siguiente comando estando dentro de la carpeta del proyecto src/:

```python
python app.py run
```

Para correr el servidor en https
```python
python app.py run --https
```

Todos los parámetros de configuración del servidor están en el archivo .env, se deberán generar las claves ssl para poder ejecutar el servidor HTTPS, si las claves no existen se generará un certificado autofirmado para probar en el entorno local, requiere pyOpenSSL 24.2.1 instalado, lo puedes hacer ejecutando `pip install pyOpenSSL`

Esto iniciará el servidor en el puerto 8080. Puedes acceder a la aplicación en tu navegador web en http://localhost:8080.

Contribuir
Si deseas contribuir a este proyecto, por favor, sigue los pasos a continuación:

Haz un fork del repositorio.
Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
Realiza tus cambios y haz commit (`git commit -am 'Agrega nueva funcionalidad'`).
Haz push a la rama (`git push origin feature/nueva-funcionalida`d).
Abre un Pull Request.


Licencia
Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.
