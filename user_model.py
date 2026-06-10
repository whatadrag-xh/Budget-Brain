from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @classmethod
    def from_db(cls, db_row):
        if db_row is None:
            return None
        return cls(
            id=db_row["user_id"],
            username=db_row["username"],
        password_hash=db_row["password_hash"]
    )