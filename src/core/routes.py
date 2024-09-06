import importlib

# Diccionario de rutas para asociar las rutas con sus controladores y acciones
routes = {
    'GET': {},
    'POST': {},
    'PUT': {},
    'DELETE': {},
}

# Registra una ruta en el sistema de enrutamiento
def register_route(method, path, controller_name, action, middlewares=[]):
    try:
        # Construye la ruta del módulo correspondiente al controlador
        module_name = f'controllers.{controller_name}'
        module = importlib.import_module(module_name)

        # Obtiene la clase del controlador (sin instanciarla)
        controller_class = getattr(module, controller_name)

        # Registra la ruta en el sistema, guardando la clase del controlador y la acción
        routes[method][path] = {
            'controller': controller_class,
            'action': action,
            'middlewares': middlewares
        }
        print(f"Ruta registrada: {method} {path} -> {controller_name}@{action}")
    except ModuleNotFoundError:
        print(f"Error: El controlador '{controller_name}' no fue encontrado.")
    except AttributeError:
        print(f"Error: La acción '{action}' no existe en el controlador '{controller_name}'.")