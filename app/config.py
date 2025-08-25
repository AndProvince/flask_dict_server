import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Создаём директорию, если её нет
os.makedirs(DATA_DIR, exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-prod")

    USERS_DB_PATH = os.environ.get("USERS_DB_PATH", os.path.join(DATA_DIR, "users.db"))
    DICTS_DB_PATH = os.environ.get("DICTS_DB_PATH", os.path.join(DATA_DIR, "dictionaries.db"))
    CLIENTS_DB_PATH = os.environ.get("CLIENTS_DB_PATH", os.path.join(DATA_DIR, "clients.db"))
    DICTIONARIES_DIR = os.environ.get("DICTIONARIES_DIR", os.path.join(BASE_DIR, "dictionaries"))

    # SQLAlchemy binds
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{USERS_DB_PATH}"  # default (unused directly)
    SQLALCHEMY_BINDS = {
        "users": f"sqlite:///{USERS_DB_PATH}",
        "dicts": f"sqlite:///{DICTS_DB_PATH}",
        "clients": f"sqlite:////{CLIENTS_DB_PATH}",
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_COOKIE_CSRF_PROTECT = False  # можно включить CSRF позже
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "replace-with-strong-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)