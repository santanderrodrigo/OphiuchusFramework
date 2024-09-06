# auth_middleware.py
from core.middleware_base import MiddlewareBase
from core.response import Response
from core.session_service import SessionService

class AuthMiddleware(MiddlewareBase):
    def __init__(self, dependency_injector):
        super().__init__(dependency_injector)
        self.session_service = dependency_injector.resolve(SessionService)

    def process_request(self, handler):
        session_id = handler.cookies.get('session_id')
        if not session_id:
            return Response("Unauthorized", status=401)
        user_id = self.session_service.get_user_id(session_id)
        if not user_id:
            return Response("Unauthorized", status=401)
        handler.user_id = user_id
        return None

    def process_response(self, handler, response):
        if not handler.cookies.get('session_id'):
            session_id = self.session_service.create_session(handler.user_id)
            response.add_header('Set-Cookie', f'session_id={session_id}; HttpOnly; Path=/')
        return response