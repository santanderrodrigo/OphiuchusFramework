# middlewares/auth_middleware.py
def auth_middleware(request):
    if request.headers.get('Authorization') is None:
        return "<h1>401 Unauthorized</h1>"