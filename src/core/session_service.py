import uuid
from datetime import datetime, timedelta
import hashlib
import hmac
import secrets
import timeit
import os
import json
from core.session_storage import FileSessionStorage

class SessionService:
    CONFIG_FILE = 'core/config.json'

    def __init__(self, session_expiry=timedelta(hours=1), storage_driver=None):
        self.session_expiry = session_expiry
        self.optimal_iterations = self._load_or_find_optimal_iterations("example_password")
        self.storage = storage_driver if storage_driver else FileSessionStorage()
        self.clean_expired_sessions()

    def _load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

    def _save_config(self, config):
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)

    def _load_or_find_optimal_iterations(self, password):
        config = self._load_config()
        if 'hash_optimal_iterations' in config:
            return config['hash_optimal_iterations']

        optimal_iterations = self.find_optimal_iterations(password)
        config['hash_optimal_iterations'] = optimal_iterations
        self._save_config(config)
        
        return optimal_iterations

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

    def _measure_hash_time(self, password, iterations):
        salt = os.urandom(16)
        start_time = timeit.default_timer()
        hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        end_time = timeit.default_timer()
        return end_time - start_time

    def hash_password(self, password):
        salt = os.urandom(16)
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            self.optimal_iterations
        )
        return salt + hash_obj

    def verify_password(self, stored_password, provided_password):
        salt = stored_password[:16]
        stored_hash = stored_password[16:]
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt,
            self.optimal_iterations
        )
        return stored_hash == hash_obj

    def _generate_csrf_token(self):
        return secrets.token_urlsafe(32)

    def store_csrf_token(self, session_id, csrf_token):
        session_data = self.storage.load_session(session_id)
        if not session_data:
            session_data = {}
        session_data['csrf_token'] = csrf_token
        self.storage.save_session(session_id, session_data)

    def get_csrf_token(self, session_id):
        print("Getting CSRF token for session:", session_id)
        session_data = self.storage.load_session(session_id)
        if session_data and 'csrf_token' in session_data:
            return session_data['csrf_token']
        else:
            #egenramos un nuevo token
            csrf_token = self._generate_csrf_token()
            self.store_csrf_token(session_id, csrf_token)
            return csrf_token

    def is_valid_csrf_token(self, session_id, token):
        stored_token = self.get_csrf_token(session_id)
        print("Stored token:", stored_token, "Received token:", token)
        return stored_token and hmac.compare_digest(token, stored_token)

    def create_session(self):
        session_id = str(uuid.uuid4())
        expiry_date = datetime.utcnow() + self.session_expiry
        session_data = {'expiry_date': expiry_date.isoformat()}
        #create csrf token
        csrf_token = self._generate_csrf_token()
        session_data['csrf_token'] = csrf_token
        self.storage.save_session(session_id, session_data)
        return session_id

    def load_all_sessions(self):
        return self.storage.load_all_sessions()

    def load_session(self, session_id):
        session_data = self.storage.load_session(session_id)
        if session_data:
            if 'expiry_date' in session_data:
                expiry_date = datetime.fromisoformat(session_data['expiry_date'])
                if datetime.utcnow() < expiry_date:
                    return session_data
                else:
                    self.delete_session(session_id)
        return None

    def save_session(self, session_id, session_data):
        if session_id == "admin":
            raise Exception("No se puede guardar la sesión del usuario admin", f"session_id: {session_id}, session_data: {session_data}")
        print("Saving session:", session_id, session_data)
        session_data['expiry_date'] = (datetime.utcnow() + self.session_expiry).isoformat()
        self.storage.save_session(session_id, session_data)

    def delete_session(self, session_id):
        self.storage.delete_session(session_id)

    def clean_expired_sessions(self):
        try:
            all_sessions = self.load_all_sessions()
            for session_id, session_data in all_sessions.items():
                if 'expiry_date' in session_data:
                    expiry_date = datetime.fromisoformat(session_data['expiry_date'])
                    if datetime.utcnow() >= expiry_date:
                        self.delete_session(session_id)
        except Exception as e:
            print(f"Error cleaning expired sessions: {e}")

    def has_session(self, session_id):
        session_data = self.load_session(session_id)
        if session_data:
            return True
        return False

    def is_logged(self, session_id):
        session_data = self.load_session(session_id)
        return session_data is not None and 'username' in session_data

    def login_user(self, username, actual_session_id):
        # Regenerar la sesión si el usuario ya tiene una sesión activa
        if actual_session_id:
            session_data = self.load_session(actual_session_id)
            # Generate a new session ID to prevent session fixation
            new_session_id = str(uuid.uuid4())
            self.delete_session(actual_session_id)
        else:
            session_data = {}
            new_session_id = str(uuid.uuid4())

        session_data['username'] = username
        # Agregamos la fecha de creación de la sesión
        session_data['created_at'] = datetime.utcnow().isoformat()
        # Guardamos los datos de la sesión        
        self.save_session(new_session_id, session_data)

        return new_session_id

    def log_out(self, session_id):
        # Eliminar la sesión
        self.delete_session(session_id)
