import os
from core.helpers import Helpers

class View:
    def __init__(self, view_name, context={}):
        self.view_name = view_name
        self.context = context

    def render(self):
        # Cargamos el archivo HTML de la plantilla
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'views', self.view_name + '.html')
        print (template_path)
        try:
            with open(template_path, 'r') as file:
                template = file.read()
            # Reemplazamos los espacios reservados en la plantilla con los valores del contexto
            for key, value in self.context.items():
                template = template.replace(f'{{{{ {key} }}}}', Helpers.sanitize_text(str(value)))

            return template
        except FileNotFoundError:
            return f"<h1>Template {self.view_name} not found</h1>"
