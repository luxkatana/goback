from flask_login import UserMixin
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "goback_users"
    user_id = Column(Integer, primary_key=True)

    username = Column(String(10), nullable=False, unique=False)
    email = Column(String(254), nullable=False, unique=True)
    password = Column(String(210), nullable=False, unique=False)

    def __repr__(self) -> str:
        return f"User({self.user_id},{self.username},{self.email},{self.password})"

    def get_id(self) -> str:
        return str(self.user_id)


class JobTask(db.Model):
    __tablename__ = "goback_job_tracker"
    job_id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(User.user_id), nullable=False)
    created_at = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False, default="Working on")

    def change_status(self, new_status: str):
        self.status = new_status
