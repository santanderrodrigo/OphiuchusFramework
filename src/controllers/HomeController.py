# controllers/home_controller.py
from core.view_render import View

class HomeController:
    def index(self):
        # Lógica del controlador
        context = {
            "title": "Home Page",
            "header": "Welcome to the Home Page",
            "content": "This is the content of the home page."
        }
        return View("home", context)

    def about(self):
        # Lógica del controlador
        context = {
            "title": "About Page",
            "header": "About Us",
            "content": "This is the content of the about page."
        }
        return View("about", context)
