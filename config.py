"""Flask configuration variables."""
from os import environ, path

from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    ADMIN_PASSWORD = environ.get("ADMIN_PASSWORD")
    ADMIN_USER = environ.get("ADMIN_USER")
    SMTP_HOST = environ.get("SMTP_HOST")
    EMAIL_FROM = environ.get("EMAIL_FROM")
    EMAIL_FROM_NAME = environ.get("EMAIL_FROM_NAME")
    OPENAI_API_KEY = environ.get("OPENAI_API_KEY")
