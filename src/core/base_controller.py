# controllers/base_controller.py
from core.view_render import View
from core.response import Response
from middlewares.csrf_middleware import CSRFMiddleware

class BaseController:
    def __init__(self, handler):
        self.handler = handler
        self.cookies = handler.cookies  # Acceso a las cookies
        self.query_params = handler.query_params  # Acceso a los parámetros de la URL
        self.view = View  # Definir View como un atributo de instancia

    def get_csrf_token(self):
        csrf_token = self.cookies.get('csrf_token')
        if not csrf_token:
            csrf_token = "No CSRF token found"
        return csrf_token

    def response(self, content, status=200, content_type='text/html'):
        return Response(content, status, content_type)

    def not_found(self):
        return Response("Not found", status=404)
    
    def not_allowed(self):
        return Response("Not allowed", status=403)