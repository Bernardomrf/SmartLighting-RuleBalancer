import bcrypt

from sqlalchemy import Column, String, Boolean
from app import db

from utils import generate_id


class User(db.Model):
    __tablename__ = 'user'

    id = Column(String, unique=True, default=generate_id(), primary_key=True)
    username = Column(String, unique=True)
    active = Column(Boolean, nullable=False, default=True)
    authenticated = Column(Boolean, nullable=False, default=True)
    anonymous = Column(Boolean, nullable=False, default=False)
    pw_salt = Column(String)
    password = Column(String)

    def __init__(self, username, password):
        self.username = username
        self.pw_salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(password.encode('utf-8'), self.pw_salt)

    @property
    def is_active(self):
        return self.active

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return self.anonymous

    def get_id(self):
        return str(self.id)

    def verify_password(self, password):
        pwhash = bcrypt.hashpw(password.encode('utf-8'), self.pw_salt)
        return self.password == pwhash

    def update_password(self, password):
        self.pw_salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(password.encode('utf-8'), self.pw_salt)


# class AnonymousUser(AnonymousUserMixin, db.Model):
#     pass
