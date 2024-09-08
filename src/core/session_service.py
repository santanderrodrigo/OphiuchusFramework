import uuid
from http.cookies import SimpleCookie
from datetime import datetime, timedelta

#session stored in memory, restart server will lose all sessions
#TODO: store sessions in a database or fileSystem

class SessionService:
    def __init__(self, session_expiry=timedelta(hours=1)):
        self.sessions = {}
        self.session_expiry = session_expiry

    def create_session(self, user_id):
        session_id = str(uuid.uuid4())
        expiry_time = datetime.utcnow() + self.session_expiry
        self.sessions[session_id] = {'user_id': user_id, 'expiry': expiry_time}
        return session_id

    def get_user_id(self, session_id):
        session_data = self.sessions.get(session_id)
        if session_data and session_data['expiry'] > datetime.utcnow():
            return session_data['user_id']
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

    def set_session_cookie(self, response, session_id, is_https=False):
        try:
            secure_attr = 'Secure; ' if is_https else ''
            cookie_value = (
                f'session_id={session_id}; HttpOnly; {secure_attr}SameSite=Lax; '
                f'Path=/; Max-Age={int(self.session_expiry.total_seconds())}'
            )
            response.set_header('Set-Cookie', cookie_value)
        except Exception as e:
            print(f"Error setting session cookie: {e}")

    def delete_session_cookie(self, response):
        response.set_header('Set-Cookie', 'session_id=deleted; HttpOnly; Path=/; Max-Age=0')

    def hash_password(self, password):
        # Generamos uan sal segura
        salt = os.urandom(16)
        
        # Creamos un hash de la contraseña con el salado
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',  # Algoritmo de hash
            password.encode('utf-8'),  # Convertimos la contraseña a bytes
            salt,
            100000  #Número de iteraciones
        )
        
        # Devolvemos el salt y el hash concatenados
        return salt + hash_obj

    def verify_password(self, stored_password, provided_password):
        # Extraer el salt del stored_password
        salt = stored_password[:16]
        
        # Extraer el hash del stored_password
        stored_hash = stored_password[16:]
        
        # CreaMOS un hash del provided_password con el mismo salt
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',  # Algoritmo de hash
            provided_password.encode('utf-8'),  # Convertimos la contraseña a bytes
            salt,  # Salt
            100000  # Número de iteraciones
        )
        
        # Comparaamos el hash almacenado con el hash del provided_password y retornamos el resultado
        return stored_hash == hash_obj
        
