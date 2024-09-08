# controllers/base_controller.py
from core.view_render import View
from core.response import Response
from abc import ABC, abstractmethod
from core.session_service import SessionService
import secrets


class BaseControllerInterface(ABC):
    @abstractmethod
    def get_csrf_token(self):
        raise NotImplementedError

    @abstractmethod
    def response(self, content, status=200, content_type='text/html'):
        raise NotImplementedError

    @abstractmethod
    def json_response(self, content, status=200):
        raise NotImplementedError

    @abstractmethod
    def not_found(self):
        raise NotImplementedError
    
    @abstractmethod
    def not_allowed(self):
        raise NotImplementedError

    @abstractmethod
    def redirect(self, url, status=302):
        raise NotImplementedError

class BaseController(BaseControllerInterface):
    def __init__(self, handler, dependency_injector):
        self.handler = handler
        self.cookies = handler.cookies  # Acceso a las cookies
        self.query_params = handler.query_params  # Acceso a los parámetros de la URL
        self.post_params = handler.post_params # Acceso a los parámetros del cuerpo de la petición
        self.path_params = handler.path_params # Acceso a los parámetros de la ruta
        self.view = View  # Definir View como un atributo de instancia
        self.send_headers = []  # Almacenar las cabeceras que se deben enviar
        self.send_cookies = []  # Almacenar las cookies que se deben enviar
        self.dependency_injector = dependency_injector # Guardar el inyector de dependencias
        self.session_service = dependency_injector.resolve('SessionService')


    def get_csrf_token(self):
        # Obtener el session_id de las cookies
        session_id = self.handler.cookies.get('session_id')
        
        # Intenta obtener el token CSRF de la sesión
        csrf_token = self.session_service.get_csrf_token(session_id)
        
        if not csrf_token:
            # Si no se encuentra el token, genera uno nuevo
            csrf_token = self.session_service.generate_csrf_token()
            self.session_service.store_csrf_token(session_id, csrf_token)
            
            # Actualizar la cookie con el token CSRF
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

    def json_response(self, data, status=200):
        response = Response.json(data, status)
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

    # Métodos para redirigir a una ruta nueva
    def redirect(self, url, status=302):
        print(f'Redirecting to {url}')
        response = Response('', status, 'text/html', {'Location': url})
        for header, value in self.send_headers:
            response.set_header(header, value)
        for cookie in self.send_cookies:
            response.set_cookie(cookie[0], cookie[1])
        return response
        