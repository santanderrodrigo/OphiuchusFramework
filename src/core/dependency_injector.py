# dependency_injector.py
class DependencyInjector:
    def __init__(self):
        self._services = {}

    def register(self, name, service):
        self._services[name] = service

    def resolve(self, name):
        return self._services.get(name)