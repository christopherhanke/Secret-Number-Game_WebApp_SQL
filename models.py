import os
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite"))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    secret_number = db.Column(db.Integer, unique=True)
    password = db.Column(db.String, unique=False)
    solved = db.Column(db.String, unique=True)
    session_token = db.Column(db.String)
    deleted = db.Column(db.Boolean, unique=False)
