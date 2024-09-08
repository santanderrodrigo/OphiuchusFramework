import uuid
from http.cookies import SimpleCookie
from datetime import datetime, timedelta
import hashlib
import hmac
import secrets
import timeit
import os
import json

#session stored in memory, restart server will lose all sessions
#TODO: store sessions in a database or fileSystem

class SessionService:
    CONFIG_FILE = 'core/config.json'

    def __init__(self, session_expiry=timedelta(hours=1)):
        self.sessions = {}
        self.session_expiry = session_expiry
        self.optimal_iterations = self._load_or_find_optimal_iterations("example_password")

    def _load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

    def _save_config(self, config):
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)

    def _load_or_find_optimal_iterations(self, password):
        # Intentar cargar el valor de iteraciones óptimas desde el archivo de configuración
        config = self._load_config()
        if 'hash_optimal_iterations' in config:
            return config['hash_optimal_iterations']

        # Si no se encuentra el valor, calcularlo
        optimal_iterations = self.find_optimal_iterations(password)
        
        # Guardar el valor calculado en el archivo de configuración
        config['hash_optimal_iterations'] = optimal_iterations
        self._save_config(config)
        
        return optimal_iterations

    #Medimos el tiempo que tarda en hashear la contraseña
    def find_optimal_iterations(self, password, max_time=0.2):
        min_iterations = 1000
        max_iterations = 1000000
        print("Finding optimal iterations for password hashing...\n This may take a while")
        
        while min_iterations < max_iterations:
            mid_iterations = (min_iterations + max_iterations) // 2
            time_taken = self._measure_hash_time(password, mid_iterations)
            
            if time_taken > max_time:
                max_iterations = mid_iterations
            else:
                min_iterations = mid_iterations + 1
            
            print(f"Current range: {min_iterations} - {max_iterations}, time taken: {time_taken} seconds")
        
        optimal_iterations = min_iterations - 1
        print(f"Optimal iterations found: {optimal_iterations}")
        return optimal_iterations

    def _measure_hash_time(self,password, iterations):
        salt = os.urandom(16)
        start_time = timeit.default_timer()
        hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        end_time = timeit.default_timer()
        return end_time - start_time

    def create_session(self, user_id):
        session_id = str(uuid.uuid4())
        expiry_time = datetime.utcnow() + self.session_expiry
        self.sessions[session_id] = {'user_id': user_id, 'expiry': expiry_time}
        return session_id

    def get_user_id(self, session_id):
        session_data = self.sessions.get(session_id)
        if session_data and 'expiry' in session_data and session_data['expiry'] > datetime.utcnow():
            return session_data['user_id']
        self.destroy_session(session_id)
        return None

    def destroy_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def is_logged(self, session_id):
        session_data = self.sessions.get(session_id)
        return session_data is not None and 'expiry' in session_data and session_data['expiry'] > datetime.utcnow()

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
            self.optimal_iterations  # Número de iteraciones óptimo
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

    # CSRF protection

    def generate_csrf_token(self):
        # Generar un nuevo token CSRF
        return secrets.token_urlsafe(32)

    def store_csrf_token(self, session_id, csrf_token):
        # Almacenar el token CSRF en la sesión
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        self.sessions[session_id]['csrf_token'] = csrf_token

    def get_csrf_token(self, session_id):
        # Obtener el token CSRF almacenado en la sesión
        return self.sessions.get(session_id, {}).get('csrf_token')

    def is_valid_csrf_token(self, session_id, token):
        # Obtener el token CSRF almacenado en la sesión
        stored_token = self.get_csrf_token(session_id)

        print("Stored token:", stored_token, "Received token:", token)

        # Verificar si el token recibido coincide con el almacenado
        return stored_token and hmac.compare_digest(token, stored_token)
        
