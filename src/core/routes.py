# core.routes.py
import re
import importlib 
import inspect
from core.dependency_injector import DependencyInjector
from core.middleware_factory import MiddlewareFactory

# Diccionario de rutas para asociar las rutas con sus controladores y acciones
routes = {
    'GET': {},
    'POST': {},
    'PUT': {},
    'DELETE': {},
}

def parse_path(path):
    pattern = re.compile(r'{(\w+)}')
    matches = pattern.findall(path)
    regex_path = pattern.sub(r'(?P<\1>[^/]+)', path)
    return matches, re.compile(f'^{regex_path}$')

# Registra una ruta en el sistema de enrutamiento
def register_route(method, path, controller_name, action, middlewares=[], dependency_injector=None):
    try:
        #print(f"Registrando ruta: {method} {path} -> {controller_name}@{action}")
        # Construye la ruta del módulo correspondiente al controlador
        module_name = f'controllers.{controller_name}'
        module = importlib.import_module(module_name)

        # Obtiene la clase del controlador (sin instanciarla)
        controller_class = getattr(module, controller_name)

         # Verifica si la acción existe en la clase del controlador
        if not hasattr(controller_class, action):
            raise AttributeError(f"La acción '{action}' no existe en el controlador '{controller_name}'.")

         # Verifica si la acción acepta los parámetros requeridos
        action_method = getattr(controller_class, action)
        sig = inspect.signature(action_method)
        param_names, regex_path = parse_path(path)
        for param in param_names:
            if param not in sig.parameters:
                raise AttributeError(f"El parámetro '{param}' no es aceptado por la acción '{action}' en el controlador '{controller_name}'.")

        # Si se proporciona un inyector de dependencias, instanciar los middlewares con él
        if dependency_injector:
            middleware_factory = MiddlewareFactory(dependency_injector)
            middlewares = [middleware_factory.create(middleware) for middleware in middlewares]

        # Registra la ruta en el sistema, guardando la clase del controlador y la acción
        param_names, regex_path = parse_path(path)
        routes[method][regex_path] = {
            'controller': controller_class,
            'action': action,
            'middlewares': middlewares,
            'param_names': param_names
        }
        print(f"Ruta registrada: {method} {path} -> {controller_name}@{action}")
    except ModuleNotFoundError:
        print(f"Error: El controlador '{controller_name}' no fue encontrado.")
    except AttributeError:
        print(f"Error: La acción '{action}' no existe en el controlador '{controller_name}'.")

# Función de envoltura para registrar rutas con el inyector de dependencias
def create_route_registrar(dependency_injector):
    return lambda method, path, controller_name, action, middlewares=[]: register_route(
        method, path, controller_name, action, middlewares, dependency_injector
    )

#funcion para registarr rutas API
def create_api_route_registrar(dependency_injector):
    return lambda method, path, controller_name, action, middlewares=[]: register_route(
        method, "/api/" + path, controller_name, action, middlewares, dependency_injector
    )