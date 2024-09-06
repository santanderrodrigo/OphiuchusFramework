from abc import ABC, abstractmethod

class MiddlewareInterface(ABC):
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