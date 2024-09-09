# core/view_helper.py
import os
from core.helpers import Helpers

class ViewHelper:
    def __init__(self, view_name, context=None):
        self.view_name = view_name
        self.context = context if context is not None else {}

    def set_context(self, key, value):
        self.context[key] = value

    def render(self):
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'views', self.view_name + '.html')
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                template = file.read()
            for key, value in self.context.items():
                template = template.replace(f'{{{{ {key} }}}}', Helpers.sanitize_text(str(value)))
            for key, value in self.context.items():
                template = template.replace(f'{{{{ !{key} }}}}', str(value))
            return template
        except FileNotFoundError:
            return f"<h1>Template {self.view_name} not found</h1>"