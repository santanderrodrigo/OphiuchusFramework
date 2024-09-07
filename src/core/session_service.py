import uuid
from http.cookies import SimpleCookie
from datetime import datetime, timedelta

class SessionService:
    def __init__(self):
        self.sessions = {}
        self.session_expiry = timedelta(hours=1)  # Expiración de sesiones de 1 hora

    def create_session(self, user_id):
        session_id = str(uuid.uuid4())
        expiry_time = datetime.utcnow() + self.session_expiry
        self.sessions[session_id] = {'user_id': user_id, 'expiry': expiry_time}
        return session_id

    def get_user_id(self, session_id):
        session_data = self.sessions.get(session_id)
        if session_data and session_data['expiry'] > datetime.utcnow():
            return session_data['user_id']
        else:
            self.destroy_session(session_id)
            return None

    def destroy_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def is_logged(self, session_id):
        session_data = self.sessions.get(session_id)
        return session_data is not None and session_data['expiry'] > datetime.utcnow()

    def parse_session_cookie(self, cookie_header):
        cookie = SimpleCookie(cookie_header)
        return cookie.get('session_id').value if 'session_id' in cookie else None

    def regenerate_session_id(self, old_session_id):
        user_id = self.get_user_id(old_session_id)
        if user_id:
            self.destroy_session(old_session_id)
            return self.create_session(user_id)
        return None