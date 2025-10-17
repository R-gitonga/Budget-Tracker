import os
import secrets


class Config:
    # generate a random secret key only if not provided via environment variable

    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///budget.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False