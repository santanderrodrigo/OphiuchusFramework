import os
import hmac
import hashlib
from urllib.parse import parse_qs
from core.response import Response
from core.middleware_base import MiddlewareBase

class CSRFMiddleware(MiddlewareBase):
    def process_request(self, handler):
        # Verificar el token CSRF en solicitudes POST
        if handler.command == 'POST':
            print("Handling POST request")
            csrf_token = handler.post_params.get('csrf_token', [None])[0]
            if not csrf_token or not self._is_valid_token(handler, csrf_token):
                print("Invalid CSRF token")
                return Response('CSRF token is invalid', 403)
        return None
        

    def process_response(self, handler, response):
        # Verificar si ya existe un token CSRF en las cookies
        if 'csrf_token' not in handler.cookies:
            csrf_token = self._generate_csrf_token()
            response.set_cookie('csrf_token', csrf_token)
        return response

    def _generate_csrf_token(self):
        # Generar un nuevo token CSRF
        return hmac.new(os.urandom(16), digestmod=hashlib.sha256).hexdigest()

    def _is_valid_token(self, handler, token):
        # Obtener el token CSRF almacenado en las cookies
        stored_token = handler.cookies.get('csrf_token')

        print("Stored token:", stored_token, "Received token:", token)

        # Verificar si el token recibido coincide con el almacenado
        return stored_token and hmac.compare_digest(token, stored_token)

       
