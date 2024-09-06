# session_service.py
import uuid
from http.cookies import SimpleCookie

class SessionService:
    def __init__(self):
        self.sessions = {}

    def create_session(self, user_id):
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = user_id
        return session_id

    def get_user_id(self, session_id):
        return self.sessions.get(session_id)

    def destroy_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def is_logged(self, session_id):
        return session_id in self.sessions

    def parse_session_cookie(self, cookie_header):
        cookie = SimpleCookie(cookie_header)
        return cookie.get('session_id').value if 'session_id' in cookie else None