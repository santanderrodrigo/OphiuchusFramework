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
        # Carga dinámicamente el módulo del controlador
        module = importlib.import_module(module_name)
        # Obtiene la clase del controlador
        controller_class = getattr(module, controller_name)
        # Instancia el controlador
        controller_instance = controller_class()
        # Agrega la ruta, su acción y middlewares al diccionario de rutas para el método específico
        routes[method][path] = {
            'action': getattr(controller_instance, action),
            'middlewares': middlewares
        }
        print (f"Ruta registrada: {method} {path} -> {controller_name}@{action}")
    except ModuleNotFoundError:
        print(f"Error: El controlador '{controller_name}' no fue encontrado.")
    except AttributeError:
        print(f"Error: La acción '{action}' no existe en el controlador '{controller_name}'.")

