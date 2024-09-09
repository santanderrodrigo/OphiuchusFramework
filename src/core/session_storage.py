from abc import ABC, abstractmethod
import os
import json
from datetime import datetime
import hashlib
import base64

class SessionStorage(ABC):
    @abstractmethod
    def save_session(self, session_id, session_data):
        pass

    @abstractmethod
    def load_session(self, session_id):
        pass

    @abstractmethod
    def delete_session(self, session_id):
        pass

    @abstractmethod
    def load_all_sessions(self):
        pass


class FileSessionStorage(SessionStorage):
    def __init__(self, file_path='sessions.json'):
        self.file_path = file_path
        self.app_key = os.getenv('APP_KEY', 'default_key')
        self._load_sessions()

    def _load_sessions(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    encrypted_sessions = json.load(f)
                    self.sessions = {
                        session_id: self._decrypt(session_data)
                        for session_id, session_data in encrypted_sessions.items()
                    }
                    # Convertir las fechas de expiración a objetos datetime
                    for session_id, session_data in self.sessions.items():
                        if 'expiry' in session_data:
                            session_data['expiry'] = datetime.fromisoformat(session_data['expiry'])
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading sessions from {self.file_path}: {e}")
                self.sessions = {}
        else:
            self.sessions = {}

    def _save_sessions(self):
        # Convertir las fechas de expiración a cadenas antes de guardar
        sessions_to_save = {
            session_id: self._encrypt({
                **data, 'expiry': data['expiry'].isoformat()
            }) if 'expiry' in data else self._encrypt(data)
            for session_id, data in self.sessions.items()
        }
        try:
            with open(self.file_path, 'w') as f:
                json.dump(sessions_to_save, f, indent=4)
        except IOError as e:
            print(f"Error saving sessions to {self.file_path}: {e}")

    def save_session(self, session_id, session_data):
        if session_id and session_id != "null":
            self.sessions[session_id] = session_data
            self._save_sessions()

    def load_session(self, session_id):
        return self.sessions.get(session_id)

    def load_all_sessions(self):
        return self.sessions or {}

    def delete_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()

    def _get_cipher_key(self):
        return hashlib.sha256(self.app_key.encode()).digest()

    def _encrypt(self, data):
        cipher_key = self._get_cipher_key()
        json_data = json.dumps(data)  # Convert dictionary to JSON string
        encoded_data = base64.b64encode(json_data.encode())
        return base64.b64encode(encoded_data + cipher_key).decode()

    def _decrypt(self, data):
        cipher_key = self._get_cipher_key()
        decoded_data = base64.b64decode(data.encode())
        json_data = base64.b64decode(decoded_data[:-len(cipher_key)]).decode()
        return json.loads(json_data)