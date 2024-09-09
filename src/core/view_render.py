# core/view_render.py
import os
from core.helpers import Helpers
from http.cookies import SimpleCookie

class View:
    def __init__(self, view_name, context=None, content_type='text/html', headers=None):
        self.view_name = view_name
        self.context = context if context is not None else {}
        self.headers = {'Content-Type': content_type}
        if headers:
            self.headers.update(headers)
        self.cookies = SimpleCookie()

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

    def set_cookie(self, key, value, path='/', httponly=True, secure=False, expires=None):
        self.cookies[key] = value
        self.cookies[key]['path'] = path
        self.cookies[key]['httponly'] = httponly
        if secure:
            self.cookies[key]['secure'] = True
        if expires:
            self.cookies[key]['expires'] = expires

    def delete_cookie(self, key, path='/'):
        self.cookies[key] = ''
        self.cookies[key]['path'] = path
        self.cookies[key]['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'

    def get_cookie(self, key):
        return self.cookies.get(key)

    def get_headers(self):
        headers = self.headers.copy()
        if self.cookies:
            headers['Set-Cookie'] = self.cookies.output(header='', sep='; ')
        return headers

    def set_header(self, header, value):
        self.headers[header] = value