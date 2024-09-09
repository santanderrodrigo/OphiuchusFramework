# core/base_controller.py
from core.view_helper import ViewHelper
from core.response_helper import ResponseHelper
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
        self.cookies = handler.cookies
        self.query_params = handler.query_params
        self.post_params = handler.post_params
        self.path_params = handler.path_params
        self.response_helper = ResponseHelper()
        self.dependency_injector = dependency_injector
        self.session_service = dependency_injector.resolve('SessionService')

    def get_csrf_token(self):
        session_id = self.handler.cookies.get('session_id')
        print(f"BASE Session ID: {session_id}")
        csrf_token = self.session_service.get_csrf_token(session_id)
        if not csrf_token:
            print("No CSRF token found, generating a new one")
        return csrf_token

    def response(self, content, status=200, content_type='text/html'):
        return self.response_helper.html_response(content, status)

    def json_response(self, data, status=200):
        return self.response_helper.json_response(data, status)

    def not_found(self):
        return self.response_helper.not_found_response()
    
    def not_allowed(self):
        return self.response_helper.not_allowed_response()

    def redirect(self, url, status=302):
        print(f'Redirecting to {url}')
        return self.response_helper.redirect_response(url, status)

    def add_cookie(self, key, value, path='/', httponly=True, secure=False, expires=None):
        self.response_helper.set_cookie(key, value, path, httponly, secure, expires)

    def add_header(self, header, value):
        self.response_helper.set_header(header, value)

    def render_view(self, view_name, context=None):
        view_helper = ViewHelper(view_name, context)
        content = view_helper.render()
        return self.response(content)