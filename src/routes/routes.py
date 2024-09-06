from core.routes import routes, register_route
from middlewares.auth_middleware import auth_middleware  # Importa el middleware

# Registra rutas con el controlador y acción correspondientes
register_route('GET', '/', 'HomeController', 'index')
register_route('GET', '/about', 'HomeController', 'about')
register_route('GET', '/text', 'DashboardController', 'show_dashboard')

# Puedes registrar más rutas aquí...