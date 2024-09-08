from core.base_controller import BaseController

class UsersController(BaseController):
    def __init__(self, handler, dependency_injector):
        super().__init__(handler, dependency_injector)
        # Obtenemos el service de la session
        self._session_service = dependency_injector.resolve('SessionService')

    def index(self):
        users = [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'},
            {'id': 3, 'name': 'Charlie'},
        ]
        return self.json_response(users)

    def create(self):
        return self.json_response({'message': 'User created'})

    def show(self, id):
        if id == '1':
            user = {'id': id, 'name': 'Bob'}
        else:
            #not content
            return self.not_found()
        return self.json_response(user)

