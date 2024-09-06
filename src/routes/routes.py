# routes_config.py
from middlewares.auth_middleware import AuthMiddleware
from core.middleware_factory import MiddlewareFactory
from core.routes import create_route_registrar

def register_routes(injector):
    # Crear la función de registro de rutas con el inyector de dependencias
    register_route_with_injector = create_route_registrar(injector)

    # Registra rutas con el controlador y acción correspondientes
    register_route_with_injector('GET', '/', 'HomeController', 'index')
    register_route_with_injector('GET', '/about', 'HomeController', 'about')
    register_route_with_injector('GET', '/text', 'DashboardController', 'show_dashboard', [AuthMiddleware])
    register_route_with_injector('POST', '/submit', 'DashboardController', 'submit_text')
    # Puedes registrar más rutas aquí...