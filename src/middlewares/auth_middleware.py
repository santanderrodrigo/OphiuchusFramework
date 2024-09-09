# auth_middleware.py
from core.middleware_base import MiddlewareBase
from core.response import Response
from core.session_service import SessionService

class AuthMiddleware(MiddlewareBase):
    def __init__(self, dependency_injector):
        super().__init__(dependency_injector)
        self.session_service = dependency_injector.resolve('SessionService')
        
    def process_request(self, handler):
        session_id = handler.cookies.get('session_id')
        print("AUTHMIddleware Session id: ", session_id)
        handler.user_id = None
        
        if session_id:
            try:
                is_logged = self.session_service.is_loggued(session_id)
                if is_logged:
                    print("User is logged")
                    session_data = self.session_service.load_session(session_id)
                    handler.user_id = session_data.get('username')
                else:
                    print("User is not logged")
                    #self.session_service.delete_session(session_id)
            except Exception as e:
                handler.user_id = None
        
        if not handler.user_id:
            return self.redirect(f'/login?next={handler.path}')
        
        return None

    def process_response(self, handler, response):
        return response