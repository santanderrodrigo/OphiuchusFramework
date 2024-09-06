from abc import ABC, abstractmethod
from core.dependency_injector import DependencyInjector
from core.response import Response

class MiddlewareInterface(ABC):
    def __init__(self, dependency_injector):
        self.dependency_injector = dependency_injector

    @abstractmethod
    def process_request(self, request):
        pass

    @abstractmethod
    def process_response(self, handler, response):
        pass


class MiddlewareBase(MiddlewareInterface):
    def process_request(self, request):
        return request

    def process_response(self, handler, response):
        return response

    # Métodos para redirigir a una ruta nueva
    def redirect(self, url, status=302):
        print(f'Redirecting to {url}')
        response = Response('', status, 'text/html', {'Location': url})
        return response