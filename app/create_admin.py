from app.models import AdminUser
import uuid

from config import Config
from . import db


def create_admin():
    email = Config.ADMIN_USER
    password = Config.ADMIN_PASSWORD

    existing_admin = AdminUser.query.filter(
        AdminUser.email == email
    ).first()

    if existing_admin:
        return

    new_admin = AdminUser(
        email=email,
        password=AdminUser.get_hashed_pass(password),
        access_token=uuid.uuid4().hex,
    )
    db.session.add(new_admin)
    db.session.commit()
