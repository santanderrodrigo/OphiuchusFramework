from core.database.crud_base import CRUDBase

class User(CRUDBase):
    table_name = "users"

    def __init__(self, id, username, email, hashed_password):
        self.id = id
        self.username = username
        self.email = email
        self.hashed_password = hashed_password

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"