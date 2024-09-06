from http.server import BaseHTTPRequestHandler, HTTPServer
from core.routes import routes
from core.middleware_manager import MiddlewareManager

global_middlewares = []
# Crear una instancia global de MiddlewareManager
middleware_manager = MiddlewareManager()

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')

    def handle_request(self, method):
        try:
            # Ejecuta los middlewares globales
            middleware_response = self.execute_middlewares(global_middlewares)
            if middleware_response:
                self.send_response(401)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(middleware_response.encode())
                return

            # Verifica si la ruta existe
            if method in routes and self.path in routes[method]:
                route_info = routes[method][self.path]
                
                # Ejecuta los middlewares específicos de la ruta
                middleware_response = self.execute_middlewares(route_info['middlewares'])
                if middleware_response:
                    self.send_response(401)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(middleware_response.encode())
                    return

                # Ejecuta la acción del controlador
                controller_function = route_info['action']
                response = controller_function()
                if hasattr(response, 'render'):
                    response = response.render()  # Convertimos a string el objeto de tipo View
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(response.encode())
            else:
                self.send_error(404, 'Page not found')
        except Exception as e:
            self.send_error(500, f'Internal server error: {str(e)}')

    def execute_middlewares(self, middlewares):
        for middleware in middlewares:
            if callable(middleware):
                response = middleware(self)
                if response:
                    return response
            else:
                print(f"Error: Middleware {middleware} is not callable")
        return None
    

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    middleware_manager.load_middlewares()
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()