from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "goback_users"
    user_id = Column(Integer, primary_key=True)

    username = Column(String(10), nullable=False, unique=True)
    email = Column(String(254), nullable=False, unique=True)
    password = Column(String(210), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"User({self.user_id},{self.username},{self.email},{self.password})"

    def get_id(self) -> str:
        return str(self.user_id)
