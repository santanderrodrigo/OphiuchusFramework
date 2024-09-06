# router.py
from http.server import BaseHTTPRequestHandler, HTTPServer
from core.routes import routes
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
        #try:
            # Ejecuta los middlewares globales
            middleware_response = self.execute_middlewares(global_middlewares)
            if middleware_response:
                response = Response(middleware_response, status=401)
                self.send_response(response.status)
                for header, value in response.get_headers().items():
                    self.send_header(header, value)
                self.end_headers()
                self.wfile.write(response.content.encode())
                return

            if method in routes and self.path in routes[method]:
                route_info = routes[method][self.path]
                middleware_response = self.execute_middlewares(route_info['middlewares'])
                if middleware_response:
                    response = Response(middleware_response, status=401)
                    self.send_response(response.status)
                    for header, value in response.get_headers().items():
                        self.send_header(header, value)
                    self.end_headers()
                    self.wfile.write(response.content.encode())
                    return

                controller_function = route_info['action']
                response_content = controller_function()
                if hasattr(response_content, 'render'):
                    response_content = response_content.render()

                response = Response(response_content)
                csrf_middleware = CSRFMiddleware()
                response = csrf_middleware.process_response(self, response)

                self.send_response(response.status)
                for header, value in response.get_headers().items():
                    self.send_header(header, value)
                self.end_headers()
                self.wfile.write(response.content.encode())
            else:
                self.send_error(404, 'Page not found')
        #except Exception as e:
            #self.send_error(500, f'Internal server error: {str(e)}')

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

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    # Instanciar el CSRFMiddleware
    csrf_middleware = CSRFMiddleware()
    # Registrar el CSRFMiddleware como un middleware global
    global_middlewares.append(csrf_middleware.process_request)
   
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()