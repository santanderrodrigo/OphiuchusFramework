from core.base_controller import BaseController

class DashboardController(BaseController):
    def show_dashboard(self):
        csrf_token = self.get_csrf_token()
        form_html = f"""
        <form method="POST" action="/submit">
            <input type="hidden" name="csrf_token" value="{csrf_token}">
            <input type="text" name="example_field" placeholder="Example Field">
            <button type="submit">Submit</button>
        </form>
        """
        return self.response(content=form_html, status=200, content_type='text/html')

    def submit_text(self):
        return self.response(content = "Text submitted successfully")

