# core/dependency_injector.py
class DependencyInjector:
    def __init__(self):
        self._services = {}

    def register(self, service_class, instance):
        self._services[service_class] = instance

    def resolve(self, service_class):
        return self._services.get(service_class)

    def resolve_all(self):
        return self._services