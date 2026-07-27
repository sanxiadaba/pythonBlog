from sqlalchemy import select, text
from werkzeug.security import generate_password_hash

from extensions import db


def initialize_database():
    """Create missing tables without destroying existing data."""
    db.create_all()


def ininDatabase():
    """Backward-compatible alias for the original misspelled function."""
    initialize_database()


def create_user(username, password, role="user", nickname=None):
    users = db.metadata.tables["users"]
    existing = db.session.execute(select(users.c.userid).where(users.c.username == username)).first()
    if existing:
        raise ValueError(f"User already exists: {username}")
    result = db.session.execute(
        users.insert().values(
            username=username,
            password=generate_password_hash(password, method="scrypt"),
            nickname=nickname or username.split("@", 1)[0],
            avatar="default/1.png",
            role=role,
            credit=50,
            apply=0,
            agreeEditor=1 if role in {"admin", "editor"} else 0,
            forbidLogin=0,
        )
    )
    db.session.commit()
    return result.inserted_primary_key[0]


def watchVersionOfMysql():
    try:
        return str(db.session.execute(text("select version()")).scalar_one())
    except Exception:
        db.session.rollback()
        return "unavailable"
