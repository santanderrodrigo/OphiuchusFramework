import os
import hmac
import hashlib
from urllib.parse import parse_qs

class CSRFMiddleware:
    def __init__(self):
        #obtenemos de la vatriable de entorno el valor de la clave secreta
        self.secret_key = "fsdfsdfsdfsdf"
        print(f"CSRF Middleware initialized with secret key: {self.secret_key}") 
        if not self.secret_key:
            raise ValueError("APP_KEY environment variable not set")

    def _generate_csrf_token(self):
        return hmac.new(self.secret_key.encode(), os.urandom(64), hashlib.sha256).hexdigest()

    def _get_csrf_token_from_request(self, request):
        # Obtener cookies del encabezado
        cookies = {}
        if 'Cookie' in request.headers:
            cookie_header = request.headers['Cookie']
            cookies = dict(cookie.split('=') for cookie in cookie_header.split('; '))

        # Obtener datos del formulario del cuerpo de la solicitud
        content_length = int(request.headers.get('Content-Length', 0))
        post_data = request.rfile.read(content_length).decode('utf-8')
        form_data = parse_qs(post_data)

        print("formData => " , form_data.get('csrf_token', [None])[0], "cookies => ", cookies.get('csrf_token'))

        return cookies.get('csrf_token'), form_data.get('csrf_token', [None])[0]

    def process_request(self, request):
        print("CSRF Middleware process_request")
        if request.command == 'POST':
            cookie_token, form_token = self._get_csrf_token_from_request(request)
            if not cookie_token or not form_token or cookie_token != form_token:
                raise ValueError("CSRF token missing or incorrect")

    def process_response(self, request, response):
        csrf_token = self._generate_csrf_token()
        response.set_cookie('csrf_token', csrf_token)
        return response