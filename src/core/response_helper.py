# core/response_helper.py
from http.cookies import SimpleCookie
from core.response import Response

class ResponseHelper:
    def __init__(self):
        self.headers = {}
        self.cookies = SimpleCookie()

    def set_header(self, header, value):
        self.headers[header] = value

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

    def get_headers(self):
        headers = self.headers.copy()
        if self.cookies:
            headers['Set-Cookie'] = self.cookies.output(header='', sep='; ')
        return headers

    def html_response(self, content, status=200):
        response = Response(content, status, 'text/html', self.get_headers())
        return response

    def json_response(self, data, status=200):
        response = Response.json(data, status)
        response.headers.update(self.get_headers())
        return response

    def redirect_response(self, location, status=302):
        response = Response.redirect(location, status)
        response.headers.update(self.get_headers())
        return response

    def not_found_response(self):
        return self.html_response("Not found", status=404)

    def not_allowed_response(self):
        return self.html_response("Not allowed", status=403)