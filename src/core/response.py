from http.cookies import SimpleCookie

class Response:
    def __init__(self, content='', status=200, content_type='text/html', headers=None):
        self.content = content
        self.status = status
        self.headers = {'Content-Type': content_type}
        if headers:
            self.headers.update(headers)
        self.cookies = SimpleCookie()

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

    @staticmethod
    def json(data, status=200):
        import json
        content = json.dumps(data)
        return Response(content, status, content_type='application/json')

    @staticmethod
    def text(content, status=200):
        return Response(content, status, content_type='text/plain')

    @staticmethod
    def html(content, status=200):
        return Response(content, status, content_type='text/html')

    @staticmethod
    def redirect(location, status=302):
        response = Response('', status, content_type='text/html')
        response.set_header('Location', location)
        return response