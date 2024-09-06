import os
import importlib

class MiddlewareManager:

    def __init__(self):
        self.middlewares = []
        self.global_middlewares = []
        

    def load_middlewares(self):
        """Cargar todos los middlewares desde la carpeta 'middlewares'."""
        print('Cargando middlewares...')
        middleware_dir = os.path.join(os.path.dirname(__file__), '../middlewares')
        for filename in os.listdir(middleware_dir):
            if filename.endswith('_middleware.py'):
                print(f'Cargando middleware: {filename}')
                module_name = f'middlewares.{filename[:-3]}'  # Nombre del módulo sin '.py'
                module = importlib.import_module(module_name)
                for attr in dir(module):
                    if callable(getattr(module, attr)) and attr.endswith('_middleware'):
                        self.add_middleware(getattr(module, attr))

    def register_global_middleware(self, middleware):
        """Registrar un middleware global."""
        self.global_middlewares.append(middleware)

    def add_middleware(self, middleware):
        """Registrar un nuevo middleware."""
        self.middlewares.append(middleware)

    def process(self, request):
        """Ejecutar cada middleware con la solicitud actual."""
        print('Ejecutando middlewares...')
        for middleware in self.middlewares:
            result = middleware(request)
            if result is not None:
                return result  # Si algún middleware devuelve algo, detener procesamiento
        return None

