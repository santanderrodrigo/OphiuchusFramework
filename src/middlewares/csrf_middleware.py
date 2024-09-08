from core.response import Response
from core.middleware_base import MiddlewareBase
from core.session_service import SessionService

class CSRFMiddleware(MiddlewareBase):
    def __init__(self, dependency_injector):
        super().__init__(dependency_injector)
        self.session_service = dependency_injector.resolve('SessionService')

    def process_request(self, handler):
        # Verificar el token CSRF en solicitudes POST
        if handler.command == 'POST':
            print("Handling POST request")
            csrf_token = handler.post_params.get('csrf_token', [None])[0]
            session_id = handler.cookies.get('session_id')
            if not csrf_token or not self.session_service.is_valid_csrf_token(session_id, csrf_token):
                print("Invalid CSRF token")
                return Response('CSRF token is invalid', 403)
        return None

    def process_response(self, handler, response):
        # Verificar si ya existe un token CSRF en las cookies
        session_id = handler.cookies.get('session_id')
        if not session_id or not self.session_service.get_csrf_token(session_id):
            csrf_token = self.session_service.generate_csrf_token()
            print("Generated new CSRF token:", csrf_token)
            self.session_service.store_csrf_token(session_id, csrf_token)
            response.set_cookie('csrf_token', csrf_token)
        return response