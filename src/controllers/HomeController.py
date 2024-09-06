# controllers/home_controller.py
from core.base_controller import BaseController
from core.session_service import SessionService



class HomeController(BaseController):
    def __init__(self, handler, dependency_injector):
        super().__init__(handler, dependency_injector)
        # Obtenemos el service de la session
        self._session_service = dependency_injector.resolve('SessionService')
        
        

    def index(self):
        # Lógica del controlador
        context = {
            "title": "Home Page",
            "header": "Welcome to the Home Page",
            "content": "This is the content of the home page."
        }
        return self.view("home", context)

    def about(self):
        self._session_service.create_session("user_id")
        # Lógica del controlador
        context = {
            "title": "About Page",
            "header": "About Us",
            "content": "This is the content of the about page."
        }
        return self.view("about", context)
