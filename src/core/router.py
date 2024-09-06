# router.py
from http.server import BaseHTTPRequestHandler, HTTPServer
from core.routes import routes
from http.cookies import SimpleCookie
from core.utils import load_env_file
from middlewares.csrf_middleware import CSRFMiddleware
from core.response import Response

load_env_file('.env')
global_middlewares = []

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')

    def handle_request(self, method):
        try:
            self.parse_cookies()
            self.parse_query_string()
            
            if method in routes and self.path in routes[method]:
                route_info = routes[method][self.path]

                # Ejecuta los middlewares de la ruta
                middleware_response = self.execute_middlewares(route_info['middlewares'])
                if middleware_response:
                    self._send_response(middleware_response)
                    return

                # Instanciar el controlador con el request y los datos
                controller_class = route_info['controller']
                controller_instance = controller_class(self)

                # Invocar la función del controlador
                controller_function = getattr(controller_instance, route_info['action'])
                response = controller_function()

                # Si el controlador no devuelve una instancia de Response, crear una
                if not isinstance(response, Response):
                    response_content = response
                    if hasattr(response_content, 'render'):
                        response_content = response_content.render()
                    response = Response(response_content)

                self._send_response(response)
            else:
                self.send_error(404, 'Page not found')

        except Exception as e:
            self.send_error(500, f'Internal server error: {str(e)}')

    def get_request_data(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length)
            # Parsear los datos POST si la solicitud es POST
            if self.command == 'POST':
                return parse_qs(post_data.decode('utf-8'))
        return {}

    def execute_middlewares(self, middlewares):
        for middleware in middlewares:
            print(f"Executing middleware {middleware}")
            if callable(middleware):
                response = middleware(self)
                if response:
                    return response
            else:
                print(f"Error: Middleware {middleware} is not callable")
        return None

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
        self.end_headers()
        if response.content:
            self.wfile.write(response.content.encode())

    


def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    # Instanciar el CSRFMiddleware
    csrf_middleware = CSRFMiddleware()
    # Registrar el CSRFMiddleware como un middleware global
    global_middlewares.append(csrf_middleware.process_request)
   
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()