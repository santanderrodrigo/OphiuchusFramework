# controllers/home_controller.py
from core.base_controller import BaseController

class HomeController(BaseController):
    def __init__(self, handler, dependency_injector):
        super().__init__(handler, dependency_injector)
        # Obtenemos el service de la session
        self._session_service = dependency_injector.resolve('SessionService')

    def index(self):
        # Agregar una cookie
        self.add_cookie('user_id', '12345')

        # Agregar un header
        self.add_header('X-Custom-Header', 'value')

        # Lógica del controlador
        context = {
            "title": "Home Page",
            "header": "Welcome to the Home Page",
            "content": "This is the content of the home page."
        }
        return self.render_view("home", context)

    def about(self):
        # Lógica del controlador
        context = {
            "title": "About Page",
            "header": "About Us",
            "content": "This is the content of the about page."
        }
        return self.render_view("about", context)