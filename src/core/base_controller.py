# controllers/base_controller.py
from core.view_render import View
from core.response import Response
from abc import ABC, abstractmethod
import secrets

class BaseControllerInterface(ABC):
    @abstractmethod
    def get_csrf_token(self):
        raise NotImplementedError

    @abstractmethod
    def response(self, content, status=200, content_type='text/html'):
        raise NotImplementedError

    @abstractmethod
    def not_found(self):
        raise NotImplementedError
    
    @abstractmethod
    def not_allowed(self):
        raise NotImplementedError

class BaseController(BaseControllerInterface):
    def __init__(self, handler):
        self.handler = handler
        self.cookies = handler.cookies  # Acceso a las cookies
        self.query_params = handler.query_params  # Acceso a los parámetros de la URL
        self.view = View  # Definir View como un atributo de instancia
        self.send_headers = []  # Almacenar las cabeceras que se deben enviar
        self.send_cookies = []  # Almacenar las cookies que se deben enviar

    def get_csrf_token(self):
        # Intenta obtener el token CSRF de las cookies
        csrf_token =  self.handler.cookies.get('csrf_token')
        if not csrf_token:
            # Si no se encuentra el token, genera uno nuevo
            csrf_token = secrets.token_urlsafe(32)
            self.send_cookies.append(('csrf_token', f'{csrf_token}; HttpOnly; Path=/'))
            print("No CSRF token found, generating a new one")
        return csrf_token

    def response(self, content, status=200, content_type='text/html'):
        response = Response(content, status, content_type)
        # Agregar las cabeceras y cookies que se deben enviar
        for header, value in self.send_headers:
            response.set_header(header, value)
        for cookie in self.send_cookies:
            response.set_cookie(cookie[0], cookie[1])
        return response

    def not_found(self):
        return Response("Not found", status=404)
    
    def not_allowed(self):
        return Response("Not allowed", status=403)