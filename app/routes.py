from datetime import datetime as dt
import datetime
from functools import wraps
import json
import uuid
import csv
import io
import bcrypt

from flask import make_response
from flask import current_app as app
from flask import make_response, request

from .send_email import send_email, invite_body
from .models import AdminUser, Book, QuizState, User, Event, db


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


# ###
# Authentication decorator
# ###
def user_protected_route(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.args.get(
            'access_token') or request.headers.get('access-token')

        if not token:
            return make_response("Unauthorized", 401)

        user = User.query.filter_by(access_token=token).first()

        if not user:
            return make_response("Unauthorized", 401)

        return f(user, *args, **kwargs)

    return decorator


def admin_protected_route(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.args.get(
            'access_token') or request.headers.get('access-token')

        if not token:
            return make_response("Unauthorized", 401)

        user = AdminUser.query.filter_by(access_token=token).first()

        if not user:
            return make_response("Unauthorized", 401)

        return f(*args, **kwargs)

    return decorator
# ###


@app.route("/user/create", methods=["POST"])
def user_create():
    content = request.get_json(force=True)
    params = content["params"]

    email = params.get('email')
    url = params.get('url')
    email_content = params.get('emailContent')

    subject = ""
    email_body = ""

    if email_content is not None:
        subject = email_content.get("subject")
        email_body = email_content.get("body")

    if not email:
        return make_response("Email is required!", 400)

    email = email.lower()

    existing_user = User.query.filter(
        User.email == email
    ).first()

    access_token = ""

    if existing_user:
        access_token = existing_user.access_token
    else:
        access_token = uuid.uuid4().hex

        new_user = User(
            email=email,
            access_token=access_token,
        )
        db.session.add(new_user)
        db.session.commit()

    _url = f"{url}?access_token={access_token}"

    send_email(to=email, subject=subject,
               body=invite_body(email_body, _url))

    return make_response(_url)


@app.route("/user/me", methods=["GET"])
def user_me():
    token = request.args.get(
        'access_token') or request.headers.get('access-token')

    if not token:
        return make_response("Unauthorized", 401)

    user = User.query.filter_by(access_token=token).first()

    if not user:
        return make_response("Unauthorized", 401)

    return user.toDict()


@app.route('/event', methods=['POST'])
@user_protected_route
def post_event(user: User):
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


@app.route('/state', methods=['POST'])
@user_protected_route
def post_state(user: User):
    state = request.get_json(force=True)

    if state is None:
        make_response("missing state", 400)

    book_id = state.get("book_id")

    if book_id is None:
        make_response("book_id missing in state", 400)

    state_id = QuizState.get_state_id(user.user_id, book_id)

    db_state = QuizState.query.filter_by(
        state_id=state_id
    ).first()

    if db_state:
        db_state.state = json.dumps(state)
    else:
        new_state = QuizState.create_instance(
            state_id=state_id, user_id=user.user_id, state=state)
        db.session.add(new_state)

    db.session.commit()

    return make_response(state)


@app.route('/state', methods=['GET'])
@user_protected_route
def get_state(user: User):
    book_id = request.args.get("book_id")

    state = QuizState.query.filter_by(
        state_id=QuizState.get_state_id(user.user_id, book_id)
    ).first()

    if state:
        return state.toDict()

    return make_response("No found", 404)


@app.route('/user/delete-user-data', methods=['DELETE'])
@user_protected_route
def delete_user_data(user: User):
    QuizState.query.filter_by(
        user_id=user.user_id).delete()
    Event.query.filter_by(
        user_id=user.user_id).delete()
    User.query.filter_by(
        user_id=user.user_id).delete()

    db.session.commit()

    return make_response("Ok", 200)


@app.route('/books', methods=['GET'])
@admin_protected_route
def get_books():
    books = Book.query.all()
    return {"books": [book.toDict() for book in books]}


def get_events_response(request):
    _filter = []

    event_name = request.args.get('event_name')
    date_from = request.args.get('date_from')
    date_until = request.args.get('date_until')
    book_id = request.args.get('book_id')

    if event_name:
        _filter.append(Event.event_name == event_name)
    if date_from:
        _filter.append(
            Event.created > datetime.datetime.fromtimestamp(int(date_from)/1000))
    if date_until:
        _filter.append(Event.created < datetime.datetime.fromtimestamp(
            int(date_until)/1000))
    if book_id:
        _filter.append(Event.book_id == book_id)

    events = Event.query.filter(*_filter).all()

    return [event.toDict() for event in events]


@app.route('/events', methods=['GET'])
@admin_protected_route
def get_events():
    return {"events": get_events_response(request)}


@app.route('/events/csv', methods=['GET'])
@admin_protected_route
def get_events_csv():
    events = get_events_response(request)

    output = make_response(data_to_csv_str(events))
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

    if not bcrypt.checkpw(password.encode('utf-8'), user.password):
        return make_response("Wrong email or password", 401)

    return user.toDict()
