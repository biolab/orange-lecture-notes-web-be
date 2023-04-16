"""Data models."""
import json
from . import db
import datetime
import bcrypt


class User(db.Model):
    """Data model for user accounts."""

    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), index=True, unique=True, nullable=False)
    access_token = db.Column(db.String(80), index=True, nullable=False)
    created = db.Column(db.DateTime, nullable=False,
                        default=lambda: datetime.datetime.now())

    def __repr__(self):
        return f"<Users {self.user_id}>"


class AdminUser(db.Model):
    """Data model for admin user accounts."""

    __tablename__ = "admin_users"
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), index=True, unique=True, nullable=False)
    access_token = db.Column(db.String(80), index=True, nullable=False)
    created = db.Column(db.DateTime, nullable=False,
                        default=lambda: datetime.datetime.now())
    password = db.Column(db.String(80), index=False, nullable=False)

    @classmethod
    def get_hashed_pass(cls, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def __repr__(self):
        return f"<AdminUser {self.user_id}>"


class Event(db.Model):
    """Data model for events."""

    __tablename__ = "events"
    event_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(80), index=True,
                           unique=False, nullable=False)
    book_id = db.Column(db.String(80), index=True,
                        unique=False, nullable=False)
    user_id = db.Column(db.Integer, index=True, unique=False, nullable=False)
    properties = db.Column(db.String(), index=False, nullable=False)
    created = db.Column(db.DateTime, nullable=False,
                        default=lambda: datetime.datetime.now())

    @classmethod
    def create_instance(cls, content):
        # event_name, book_id, user_id, *rest = content

        return Event(
            event_name=content.get("event_name"),
            book_id=content.get("book_id", "noId"),
            user_id=content.get("user_id", 0),
            properties=json.dumps(content.get("properties", {})),
        )

    def __repr__(self):
        return f"<Events {self.event_name}>"


class Book(db.Model):
    """Data model for books."""

    __tablename__ = "books"
    book_id = db.Column(db.String(80), primary_key=True)
    book_title = db.Column(db.String(80), index=True)
    url = db.Column(db.String(80), index=False)
    created = db.Column(db.DateTime, nullable=False,
                        default=lambda: datetime.datetime.now())

    def __repr__(self):
        return f"<Books {self.book_id}>"

