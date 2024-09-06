# controllers/home_controller.py
from core.base_controller import BaseController


class HomeController(BaseController):
    def index(self):
        # Lógica del controlador
        context = {
            "title": "Home Page",
            "header": "Welcome to the Home Page",
            "content": "This is the content of the home page."
        }
        return self.view("home", context)

    def about(self):
        # Lógica del controlador
        context = {
            "title": "About Page",
            "header": "About Us",
            "content": "This is the content of the about page."
        }
        return self.view("about", context)
