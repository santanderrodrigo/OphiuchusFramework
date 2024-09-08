# routes_config.py
from middlewares.auth_middleware import AuthMiddleware
from core.middleware_factory import MiddlewareFactory
from core.routes import create_route_registrar, create_api_route_registrar

def register_routes(injector):
    # Crear la función de registro de rutas con el inyector de dependencias
    add_route = create_route_registrar(injector)
    add_api_route = create_api_route_registrar(injector)

    # Registra rutas con el controlador y acción correspondientes
    add_route('GET', '/', 'HomeController', 'index')
    add_route('GET', '/dashboard', 'DashboardController', 'show_dashboard', [AuthMiddleware])
    add_route('GET', '/login', 'LoginController', 'show')
    add_route('POST', '/login', 'LoginController', 'login')
    add_route('GET', '/logout', 'LoginController', 'logout')
    add_route('GET', '/about', 'HomeController', 'about')

    # Registra rutas de la API
    add_api_route('GET', 'users', 'UsersController', 'index2')
    add_api_route('POST', 'users', 'UsersController', 'create')
    add_api_route('GET', 'users/{id}', 'UsersController', 'show')

    # Puedes registrar más rutas aquí... 