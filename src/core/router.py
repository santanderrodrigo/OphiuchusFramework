import os
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from core.routes import routes as routes_dict, create_route_registrar
from http.cookies import SimpleCookie
from core.utils import load_env_file
from middlewares.csrf_middleware import CSRFMiddleware
from middlewares.auth_middleware import AuthMiddleware
from core.response import Response
from core.middleware_base import MiddlewareInterface
from core.dependency_injector import DependencyInjector
from core.middleware_factory import MiddlewareFactory
from core.session_service import SessionService
import routes.routes as routes_config

load_env_file('.env')
global_middlewares = []

# Crear una instancia del inyector de dependencias
injector = DependencyInjector()
# Crear una instancia de la fábrica de middlewares
middleware_factory = MiddlewareFactory(injector)

# Instanciar el CSRFMiddleware usando la fábrica
csrf_middleware = middleware_factory.create(CSRFMiddleware)
# Registrar el CSRFMiddleware como un middleware global
global_middlewares.append(csrf_middleware)

# Instanciar el servicio de sesión
session_service = SessionService()
# Registrar el servicio de sesión en el inyector de dependencias
injector.register('SessionService', session_service)

# Crear la función de registro de rutas con el inyector de dependencias
register_route_with_injector = create_route_registrar(injector)
# Pasar el inyector de dependencias a la configuración de rutas
routes_config.register_routes(injector)

print(f"SessionService registered: {injector.resolve('SessionService')}")

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')

    def handle_request(self, method):
        try:
            if self.path.startswith('/assets/'):
                self.serve_static_file()
            else:
                self.handle_dynamic_request(method)
        except Exception as e:
            self.send_error(500, f'Internal server error: {str(e)}')

    def serve_static_file(self):
        file_path = self.path.lstrip('/')
        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            self.set_content_type(file_path)
            self.end_headers()
            with open(file_path, 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_error(404, 'File not found')

    def set_content_type(self, file_path):
        if file_path.endswith('.css'):
            self.send_header('Content-Type', 'text/css')
        elif file_path.endswith('.js'):
            self.send_header('Content-Type', 'application/javascript')
        elif file_path.endswith('.png'):
            self.send_header('Content-Type', 'image/png')
        elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
            self.send_header('Content-Type', 'image/jpeg')
        elif file_path.endswith('.gif'):
            self.send_header('Content-Type', 'image/gif')
        elif file_path.endswith('.svg'):
            self.send_header('Content-Type', 'image/svg+xml')
        elif file_path.endswith('.ico'):
            self.send_header('Content-Type', 'image/x-icon')
        else:
            self.send_header('Content-Type', 'application/octet-stream')

    def handle_dynamic_request(self, method):
        self.parse_cookies()
        self.parse_query_string()
        self.post_params = self.get_request_data()

        if method in routes_dict and self.path in routes_dict[method]:
            route_info = routes_dict[method][self.path]

            # Ejecuta los middlewares globales
            middleware_response = self.execute_middlewares(global_middlewares, 'request')
            if middleware_response:
                self._send_response(middleware_response)
                return

            # Ejecuta los middlewares de la ruta
            middleware_response = self.execute_middlewares(route_info['middlewares'], 'request')
            if middleware_response:
                self._send_response(middleware_response)
                return

            # Instanciar el controlador con el request y los datos
            controller_class = route_info['controller']
            controller_instance = controller_class(self, dependency_injector=injector)

            # Invocar la función del controlador
            controller_function = getattr(controller_instance, route_info['action'])
            response = controller_function()

            # Si el controlador no devuelve una instancia de Response, crear una
            if not isinstance(response, Response):
                response_content = response
                if hasattr(response_content, 'render'):
                    response_content = response_content.render()
                response = Response(response_content)

            # Ejecuta los middlewares de la respuesta
            response = self.execute_middlewares(route_info['middlewares'], 'response', response)

            # Ejecuta los middlewares globales de la respuesta
            response = self.execute_middlewares(global_middlewares, 'response', response)

            self._send_response(response)
        else:
            # Verificar si la ruta existe para otros métodos
            allowed_methods = [m for m in routes_dict if self.path in routes_dict[m]]
            if allowed_methods:
                self.send_error(405, 'Method Not Allowed')
            else:
                self.send_error(404, 'Page not found')

    def get_request_data(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length)
            # Parsear los datos POST si la solicitud es POST
            if self.command == 'POST':
                return parse_qs(post_data.decode('utf-8'))
        return {}

    def execute_middlewares(self, middlewares, phase, response=None):
        for middleware in middlewares:
            if isinstance(middleware, MiddlewareInterface):
                if phase == 'request':
                    response = middleware.process_request(self)
                elif phase == 'response':
                    response = middleware.process_response(self, response)
                if response:
                    return response
            else:
                print(f"Error: Middleware {middleware} does not implement MiddlewareBase")
        return response

    def parse_cookies(self):
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            cookie = SimpleCookie(cookie_header)
            self.cookies = {key: morsel.value for key, morsel in cookie.items()}
        else:
            self.cookies = {}

    def parse_query_string(self):
        self.query_params = {}
        if '?' in self.path:
            self.path, query_string = self.path.split('?')
            self.query_params = parse_qs(query_string)

    def _send_response(self, response):
        self.send_response(response.status)
        for header, value in response.get_headers().items():
            self.send_header(header, value)
        self.send_security_headers()
        self.end_headers()
        if response.content:
            self.wfile.write(response.content.encode())

    def send_security_headers(self):
        self.send_header('Content-Security-Policy', "default-src 'self'")
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()