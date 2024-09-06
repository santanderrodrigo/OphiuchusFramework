# middlewares/auth_middleware.py
from core.middleware_base import MiddlewareBase
from core.response import Response
from core.session_service import SessionService

# Crear una instancia de session_service
session_service = SessionService()

class AuthMiddleware(MiddlewareBase):
    def process_request(self, handler):
        session_id = handler.cookies.get('session_id')
        user_id = session_service.get_user_id(session_id)
        if not user_id:
            return Response("Unauthorized", status=401)
        handler.user_id = user_id
        return None

    def process_response(self, handler, response):
        if not handler.cookies.get('session_id'):
            session_id = session_service.create_session(handler.user_id)
            response.add_header('Set-Cookie', f'session_id={session_id}; HttpOnly; Path=/')
        return response