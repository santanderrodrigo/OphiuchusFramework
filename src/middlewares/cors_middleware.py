# cors_middleware.py
import os
from core.middleware_base import MiddlewareBase
from core.response import Response
from core.session_service import SessionService

# Obtener los valores de CORS desde el archivo de configuración
allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
server_HTTP_port = os.getenv('SERVER_HTTP_PORT', '8080')
server_HTTPS_port = os.getenv('SERVER_HTTPS_PORT', '8443')

# Agregar el puerto a cada origen si no está presente
allowed_origins_with_port = []
for origin in allowed_origins:
    if not origin.startswith(('http://', 'https://')):
        http_origin = f"http://{origin}"
        https_origin = f"https://{origin}"
    else:
        http_origin = origin.replace('https://', 'http://')
        https_origin = origin.replace('http://', 'https://')

    if ':' not in http_origin.split('//')[-1]:  # Verifica si el puerto no está presente
        http_origin = f"{http_origin}:{server_HTTP_port}"
    if ':' not in https_origin.split('//')[-1]:  # Verifica si el puerto no está presente
        https_origin = f"{https_origin}:{server_HTTPS_port}"

    allowed_origins_with_port.append(http_origin)
    allowed_origins_with_port.append(https_origin)

print("Allowed origins:", allowed_origins_with_port)

allowed_methods = ["GET", "POST", "PUT", "DELETE"]
allowed_headers = ["Content-Type"]

class CorsMiddleware(MiddlewareBase):
    def __init__(self, dependency_injector):
        super().__init__(dependency_injector)
        self.allowed_origins = allowed_origins_with_port or ["*"]
        self.allowed_methods = allowed_methods
        self.allowed_headers = allowed_headers

    def process_request(self, handler):
        origin = handler.headers.get('Origin')
        if not origin:
            # Permitir solicitudes sin origen para que el navegador pueda cargar archivos locales
            return None

        if origin in self.allowed_origins or "*" in self.allowed_origins:
            handler.set_header('Access-Control-Allow-Origin', origin)
            handler.set_header('Access-Control-Allow-Headers', ', '.join(self.allowed_headers))
            handler.set_header('Access-Control-Allow-Methods', ', '.join(self.allowed_methods))
            handler.set_header('Access-Control-Allow-Credentials', 'true')
        else:
            return Response("CORS Forbidden, if you are the developer, check the allowed origins configuration", status=403)

        if handler.method == 'OPTIONS':
            return Response(status=204)

        return None
    
    def process_response(self, handler, response):
        origin = handler.headers.get('Origin')
        if origin in self.allowed_origins or "*" in self.allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
            response.headers['Access-Control-Allow-Methods'] = ', '.join(self.allowed_methods)
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
