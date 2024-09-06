from core.base_controller import BaseController
from core.session_service import SessionService

class DashboardController(BaseController):
    def __init__(self, handler, dependency_injector = None):
        super().__init__(handler, dependency_injector)
        #obtenemos el service de la session
        self.session_service = dependency_injector.resolve(SessionService)

    def show_dashboard(self):

        return self.view('dashboard')

        csrf_token = self.get_csrf_token()
        form_html = f"""
        <form method="POST" action="/submit">
            <input type="hidden" name="csrf_token" value="{csrf_token}">
            <input type="text" name="example_field" placeholder="Example Field">
            <button type="submit">Submit</button>
        </form>
        """

        print("DashboardController:show_dashboard", csrf_token)

        return self.response(content=form_html, status=200, content_type='text/html')

    def submit_text(self):
        return self.response(content = "Text submitted successfully")

