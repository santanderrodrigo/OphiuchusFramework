from core.routes import routes, register_route
from middlewares.auth_middleware import AuthMiddleware  # Importa el middleware

# Registra rutas con el controlador y acción correspondientes
register_route('GET', '/', 'HomeController', 'index')
register_route('GET', '/about', 'HomeController', 'about')
register_route('GET', '/text', 'DashboardController', 'show_dashboard', [AuthMiddleware()])  # Registra el middleware
register_route('POST', '/submit', 'DashboardController', 'submit_text')

# Puedes registrar más rutas aquí...