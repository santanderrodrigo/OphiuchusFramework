# core/middleware_factory.py
from core.dependency_injector import DependencyInjector

class MiddlewareFactory:
    def __init__(self, dependency_injector: DependencyInjector):
        self.dependency_injector = dependency_injector

    def create(self, middleware_class):
        return middleware_class(self.dependency_injector)