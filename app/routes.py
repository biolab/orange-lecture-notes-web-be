"""Application routes."""
from datetime import datetime as dt, timedelta
import datetime
import uuid
import json
import time
from flask import current_app as app
from flask import make_response, request
from .models import Book, User, Event, db
from datetime import date


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
            created=dt.now(),
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


def create_event_instance(event: Event):
    return {
        "event_id": event.event_id,
        "event_name": event.event_name,
        "book_id": event.book_id,
        "user_id": event.user_id,
        "created": event.created,
        "properties": json.loads(event.properties),
    }


@app.route('/event', methods=['GET'])
def get_answers():
    start = time.time()

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

    _events = [create_event_instance(event) for event in events]

    end = time.time()
    print(f"get_answers took {end - start} seconds ")

    return {"events": _events}


@app.route('/admin/event-types', methods=['GET'])
def get_event_types():
    events = Event.query.all()
    return {"events_types": list(set([event.event_name for event in events]))}
