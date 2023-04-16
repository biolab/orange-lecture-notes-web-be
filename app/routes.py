"""Application routes."""
from datetime import datetime as dt
import datetime
from functools import wraps
import uuid
import json
import csv
import io
import bcrypt

from flask import make_response

from flask import current_app as app
from flask import make_response, request
from .models import AdminUser, Book, User, Event, db
from datetime import date


def data_to_csv_str(data: list):
    field_names = data[-1].keys()

    with io.StringIO() as s:
        writer = csv.DictWriter(
            s,
            fieldnames=field_names
        )
        writer.writeheader()
        writer.fieldnames = field_names
        for row in data:
            writer.writerow(row)

        content = s.getvalue()

    return content


@app.route("/user/create", methods=["POST"])
def user_records():
    email = request.args.get("email")

    if email is not None:
        email = email.lower()

        existing_user = User.query.filter(
            User.email == email
        ).first()
        if existing_user:
            return make_response(f"{email} already exists!")

        new_user = User(
            email=email,
            access_token=uuid.uuid4().hex,
        )
        db.session.add(new_user)  # Adds new User record to database
        db.session.commit()  # Commits all changes
        return make_response(f"User {email} created!")


@app.route('/event', methods=['POST'])
def post_event():
    content = request.get_json(force=True)

    book_id = content["book"]["book_id"]

    if book_id:
        book = Book.query.filter(Book.book_id == book_id).first()
        if not book:
            new_book = Book(
                book_id=book_id,
                book_title=content["book"]["book_title"],
                url=content["book"]["url"]
            )
            db.session.add(new_book)

    new_event = Event.create_instance(content)

    db.session.add(new_event)
    db.session.commit()

    return make_response(f"Ok")


def create_event_response(event: Event):
    return {
        "event_id": event.event_id,
        "event_name": event.event_name,
        "book_id": event.book_id,
        "user_id": event.user_id,
        "created": event.created,
        **json.loads(event.properties),
    }

# Authentication decorator


def admin_protected_route(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.args.get(
            'access_token') or request.headers.get('access-token')

        if not token:  # throw error if no token provided
            return make_response("Unauthorized", 401)

        user = AdminUser.query.filter_by(access_token=token).first()

        if not user:
            return make_response("Unauthorized", 401)

        return f(*args, **kwargs)

    return decorator


@app.route('/events', methods=['GET'])
@admin_protected_route
def get_event():
    _filter = []

    event_name = request.args.get('event_name')
    date_from = request.args.get('date_from')
    date_until = request.args.get('date_until')

    if event_name:
        _filter.append(Event.event_name == event_name)
    if date_from:
        _filter.append(
            Event.created > datetime.datetime.fromtimestamp(int(date_from)/1000))
    if date_until:
        _filter.append(Event.created < datetime.datetime.fromtimestamp(
            int(date_until)/1000))

    events = Event.query.filter(*_filter).all()

    _events = [create_event_response(event) for event in events]
    return {"events": _events}


@app.route('/events/csv', methods=['GET'])
@admin_protected_route
def get_event_csv():
    _filter = []

    event_name = request.args.get('event_name')
    date_from = request.args.get('date_from')
    date_until = request.args.get('date_until')

    if event_name:
        _filter.append(Event.event_name == event_name)
    if date_from:
        _filter.append(
            Event.created > datetime.datetime.fromtimestamp(int(date_from)/1000))
    if date_until:
        _filter.append(Event.created < datetime.datetime.fromtimestamp(
            int(date_until)/1000))

    events = Event.query.filter(*_filter).all()
    _events = [create_event_response(event) for event in events]

    output = make_response(data_to_csv_str(_events))
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route('/admin/event-types', methods=['GET'])
@admin_protected_route
def get_event_types():
    events = Event.query.all()
    return {"events_types": list(set([event.event_name for event in events]))}


@app.route('/admin/login', methods=['POST'])
def admin_login():
    content = request.get_json(force=True)
    params = content["params"]

    email = params.get('email')
    password = params.get('password')

    if not email or not password:
        return make_response("Email and password are required", 400)

    user = AdminUser.query.filter_by(email=email).first()

    if not user:
        return make_response("Wrong email or password", 401)

    hashed_pass = AdminUser.get_hashed_pass(password)

    if not bcrypt.checkpw(password.encode('utf-8'), user.password):
        return make_response("Wrong email or password", 401)

    return {
        "admin": True,
        "access_token": user.access_token,
        "email": user.email,
        "user_id": user.user_id,
    }

    return make_response(hashed_pass, 200)
