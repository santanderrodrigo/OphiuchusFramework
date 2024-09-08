#login_controller.py
from core.base_controller import BaseController

class LoginController(BaseController):
    def __init__(self, handler, dependency_injector):
        super().__init__(handler, dependency_injector)
        # Obtenemos el service de la session
        self._session_service = dependency_injector.resolve('SessionService')


    def login(self):
        # Obtenemos el usuario y contraseña del formulario post
        user = self.post_params.get('username', [None])[0]
        password = self.post_params.get('password', [None])[0]
        print(f'User: {user}, Password: {password}')

        # Validamos que el usuario y contraseña sean correctos
        if user == 'admin' and password == 'admin':
            print('Login successful for user admin')

            # Crear una nueva sesión
            session_id = self._session_service.create_session(user)
            self.send_cookies.append(('session_id', f'{session_id}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600'))

            # Redirigimos al home
            return self.redirect('/dashboard')
            
        else:
            # Mostramos un mensaje de error
            context = {
                'error': 'Usuario o contraseña incorrectos',
                'csrf_token': self.get_csrf_token()
            }
            return self.view('login', context)

    def show(self):

        #si ya esta logueado redirigir a dashboard
        session_id = self.handler.cookies.get('session_id')
        if session_id and self._session_service.is_logged(session_id):
            return self.redirect('/dashboard')

        context = {
            'csrf_token': self.get_csrf_token(),
            'error': ""
        }
        return self.view('login', context)
    
    def logout(self):
        session_id = self.handler.cookies.get('session_id')
        if session_id:
            self._session_service.destroy_session(session_id)
            self.send_cookies.append(('session_id', 'deleted; HttpOnly; Path=/; Max-Age=0'))
        return self.redirect('/login')