#login_controller.py
from core.base_controller import BaseController

class LoginController(BaseController):
    def __init__(self, handler, dependency_injector):
        super().__init__(handler, dependency_injector)
        self._session_service = dependency_injector.resolve('SessionService')

    def login(self):
        user = self.post_params.get('username', [None])[0]
        password = self.post_params.get('password', [None])[0]

        if user == 'admin' and password == 'admin':
            #obtenemos el id de la sesión desde la cookie   
            session_id = self.handler.cookies.get('session_id')
            #Hacemos login del usuario
            new_session_id = self._session_service.login_user(user, session_id)
            #guardamos la sesión en la cookie
            response = self.redirect('/dashboard')
            response.set_cookie('session_id', new_session_id)
            return response
        else:
            context = {'error': 'Usuario o contraseña incorrectos', 'csrf_token': self.get_csrf_token()}
            return self.view('login', context)

    def show(self):
        session_id = self.handler.cookies.get('session_id')
        if session_id and self._session_service.is_logged(session_id):
            return self.redirect('/dashboard')
        
        
        context = {'csrf_token': self.get_csrf_token(), 'error': ""}
        return self.view('login', context)
    
    def logout(self):
        session_id = self.handler.cookies.get('session_id')
        if session_id:
            self._session_service.delete_session(session_id)
            response = self.redirect('/')
            response.delete_cookie('session_id')
            return response

    def show_register(self):
        return self.view('register', {'csrf_token': self.get_csrf_token()})

    def register(self):
        username = self.post_params.get('username', [None])[0]
        password = self.post_params.get('password', [None])[0]
        confirm_password = self.post_params.get('confirm_password', [None])[0]

        if password != confirm_password:
            context = {'error': 'Las contraseñas no coinciden', 'csrf_token': self.get_csrf_token()}
            return self.view('register', context)

        #hacemos un hash de la contraseña con salt, ya qiue no se puede guardar la contraseña en texto plano
        hashed_password = self._session_service.hash_password(password)

        # Aquí se debería guardar el usuario en la base de datos
        return self.redirect('/login')