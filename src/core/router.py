#router.py
import os 
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from core.routes import routes as routes_dict, create_route_registrar
from http.cookies import SimpleCookie
import ssl
from middlewares.csrf_middleware import CSRFMiddleware
from core.response import Response
from core.middleware_base import MiddlewareInterface
from middlewares.cors_middleware import CorsMiddleware
from core.dependency_injector import DependencyInjector
from core.middleware_factory import MiddlewareFactory
from core.session_service import SessionService
import routes.routes as routes_config


global_middlewares = []
global_api_middlewares = []

# Crear una instancia del inyector de dependencias
injector = DependencyInjector()
# Instanciar el servicio de sesión
session_service = SessionService()
# Registrar el servicio de sesión en el inyector de dependencias
injector.register('SessionService', session_service)

# Crear una instancia de la fábrica de middlewares
middleware_factory = MiddlewareFactory(injector)
# Instanciar el CSRFMiddleware usando la fábrica
csrf_middleware = middleware_factory.create(CSRFMiddleware)
# Registrar el CSRFMiddleware como un middleware global
global_middlewares.append(csrf_middleware)
#instanciar el CorsMiddleware usando la fábrica
cors_middleware = middleware_factory.create(CorsMiddleware)
# Registrar el CorsMiddleware como un middleware global
global_middlewares.append(cors_middleware)

# Crear la función de registro de rutas con el inyector de dependencias
register_route_with_injector = create_route_registrar(injector)
# Pasar el inyector de dependencias a la configuración de rutas
routes_config.register_routes(injector)

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args,is_https=False, **kwargs):
        self.is_https = is_https
        super().__init__(*args, **kwargs)
        self.path_params = {}
        self.query_params = {}
        self.post_params = {}
        self.cookies = {}
        self.method = ''
        self.headers = {}

    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')

    def handle_request(self, method):
        #try:
            ##obtenemos los headers de la petición
            for header, value in self.headers.items():
                self.headers[header] = value
            
            #obtenemos el method de la petición
            self.method = method

            if self.path.startswith('/assets/'):
                self.serve_static_file()
            else:
                self.handle_dynamic_request(method)
        #except Exception as e:
        #    self.send_error(500, f'Internal server error: {str(e)}')

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

        for regex_path, route_info in routes_dict.get(method, {}).items():
            match = regex_path.match(self.path)
            if match:
                self.path_params = match.groupdict()

                # Determine if the route is an API route
                is_api_route = self.path.startswith('/api/')

                # Select the appropriate global middlewares
                selected_global_middlewares = global_api_middlewares if is_api_route else global_middlewares

                # Execute the selected global middlewares
                middleware_response = self.execute_middlewares(selected_global_middlewares, 'request')
                if middleware_response:
                    self._send_response(middleware_response)
                    return

                # Execute the route-specific middlewares
                middleware_response = self.execute_middlewares(route_info['middlewares'], 'request')
                if middleware_response:
                    self._send_response(middleware_response)
                    return

                # Instantiate the controller with the request and data
                controller_class = route_info['controller']
                controller_instance = controller_class(self, dependency_injector=injector)

                # Invoke the controller function with path parameters
                controller_function = getattr(controller_instance, route_info['action'])
                response = controller_function(**self.path_params)

                # If the controller does not return a Response instance, create one
                if not isinstance(response, Response):
                    response_content = response
                    if hasattr(response_content, 'render'):
                        response_content = response_content.render()
                    response = Response(response_content)

                # Execute the route-specific response middlewares
                response = self.execute_middlewares(route_info['middlewares'], 'response', response)

                # Execute the selected global response middlewares
                response = self.execute_middlewares(selected_global_middlewares, 'response', response)

                self._send_response(response)
                return

        # Si la ruta no se encuentra en las rutas definidas
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

    def set_header(self, header, value):
        #los cargamos en el self.headers
        self.headers[header] = value

    def send_security_headers(self):
        self.send_header('Content-Security-Policy', "default-src 'self'")
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')

def run_http(server_class=HTTPServer, handler_class=RequestHandler, port=8080, host='0.0.0.0'):
    server_address = ('', port)
    httpd = server_class(server_address, lambda *args, **kwargs: handler_class(*args, is_https=False, **kwargs))
    print(f'Starting HTTP server on port {port}...')
    print('Press Ctrl+C to stop the server')
    httpd.serve_forever()

def run_https(server_class=HTTPServer, handler_class=RequestHandler, port=443,  host='0.0.0.0'):
    server_address = ('', port)
    httpd = server_class(server_address, lambda *args, **kwargs: handler_class(*args, is_https=True, **kwargs))

    # Create an SSL context
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

    # Wrap the server socket with SSL
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f'Starting HTTPS server on port {port}...')
    print('Press Ctrl+C to stop the server')
    retries = 0
    max_retries = 3
    while retries < max_retries:
        try:
            httpd.serve_forever()
        except ssl.SSLError as e:
            print(f"SSL error: {e}")
            retries += 1
            print(f"Retrying in {retry_delay} seconds... ({retries}/{max_retries})")
            time.sleep(retry_delay)
        except Exception as e:
            print(f"General error: {e}")
            break
        else:
            break

def run_both(http_port=8080, https_port=8443,  host='0.0.0.0'):
    http_thread = threading.Thread(target=run_http, args=(HTTPServer, RequestHandler, http_port, host))
    https_thread = threading.Thread(target=run_https, args=(HTTPServer, RequestHandler, https_port, host))

    http_thread.start()
    https_thread.start()

    http_thread.join()
    https_thread.join()

