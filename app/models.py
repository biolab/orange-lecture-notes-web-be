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

    def toDict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "access_token": self.access_token,
            "created": self.created,
        }

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

    def toDict(self):
        return {
            "admin": True,
            "access_token": self.access_token,
            "email": self.email,
            "user_id": self.user_id,
            "created": self.created,
        }

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

    def toDict(self):
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "book_id": self.book_id,
            "user_id": self.user_id,
            "created": self.created,
            **json.loads(self.properties),
        }

    @classmethod
    def create_instance(cls, content):
        # event_name, book_id, user_id, *rest = content

        return Event(
            event_name=content.get("event_name"),
            book_id=content.get("book_id", "noId"),
            user_id=content.get("user_id"),
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

    def toDict(self):
        return {
            "book_id": self.book_id,
            "book_title": self.book_title,
            "url": self.url,
            "created": self.created,
        }

    def __repr__(self):
        return f"<Books {self.book_id}>"
