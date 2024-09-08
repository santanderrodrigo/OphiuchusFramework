# auth_middleware.py
from core.middleware_base import MiddlewareBase
from core.response import Response
from core.session_service import SessionService

class AuthMiddleware(MiddlewareBase):
    def __init__(self, dependency_injector):
        super().__init__(dependency_injector)
        self.session_service = dependency_injector.resolve('SessionService')
        

    def process_request(self, handler):
        try:
            session_id = handler.cookies.get('session_id')
            if session_id:
                user_id = self.session_service.get_user_id(session_id)
                if user_id:
                    handler.user_id = user_id
                else:
                    handler.user_id = None
            else:
                handler.user_id = None

            if handler.user_id is None:
                return self.redirect('/login')
        except Exception as e:
            return self.redirect('/login')
            
    def process_response(self, handler, response):
        try:
            if not handler.cookies.get('session_id'):
                session_id = self.session_service.create_session(handler.user_id)
                response.set_header('Set-Cookie', f'session_id={session_id}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600')
            return response
        except Exception as e:
            return response