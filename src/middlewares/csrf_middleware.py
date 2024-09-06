import os
import hmac
import hashlib
from urllib.parse import parse_qs
from core.response import Response

class CSRFMiddleware:
    def process_request(self, handler):
        # Verificar el token CSRF en solicitudes POST
        if handler.command == 'POST':
            content_length = int(handler.headers.get('Content-Length', 0))
            post_data = handler.rfile.read(content_length).decode('utf-8')
            post_params = parse_qs(post_data)
            csrf_token = post_params.get('csrf_token', [None])[0]

            if not csrf_token or not self._is_valid_token(handler, csrf_token):
                return Response("Invalid CSRF token", status=403)
        return None

    def process_response(self, handler, response):
        # Verificar si ya existe un token CSRF en las cookies
        if 'csrf_token' not in handler.cookies:
            csrf_token = self._generate_csrf_token()
            response.set_cookie('csrf_token', csrf_token)
        return response

    def _generate_csrf_token(self):
        import secrets
        return secrets.token_hex(16)

    def _is_valid_token(self, handler, token):
        # Obtener el token CSRF almacenado en las cookies
        stored_token = handler.cookies.get('csrf_token')

        # Verificar si el token recibido coincide con el almacenado
        return stored_token and hmac.compare_digest(token, stored_token)

       
