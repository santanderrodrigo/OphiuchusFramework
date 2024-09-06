class Response:
    def __init__(self, content, status=200, content_type='text/html'):
        self.content = content
        self.status = status
        self.headers = {'Content-Type': content_type}
        self.cookies = {}

    def set_cookie(self, key, value):
        self.cookies[key] = value

    def get_headers(self):
        cookie_header = '; '.join([f'{key}={value}' for key, value in self.cookies.items()])
        if cookie_header:
            self.headers['Set-Cookie'] = cookie_header
        return self.headers

    @staticmethod
    def json(data, status=200):
        import json
        content = json.dumps(data)
        return Response(content, status, content_type='application/json')
