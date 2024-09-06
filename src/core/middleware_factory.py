# core/middleware_factory.py
from core.dependency_injector import DependencyInjector
from core.middleware_base import MiddlewareInterface

class MiddlewareFactory:
    def __init__(self, dependency_injector: DependencyInjector):
        self.dependency_injector = dependency_injector

    def create(self, middleware_class):
        if issubclass(middleware_class, MiddlewareInterface):
            return middleware_class(self.dependency_injector)
        else:
            raise ValueError(f"{middleware_class} does not implement MiddlewareInterface")