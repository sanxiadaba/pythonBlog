"""Server-side storage for short-lived single-use codes.

The default Flask session is *signed but not encrypted*: anything written to it
is readable by whoever holds the cookie. Verification codes (and the login
captcha) therefore live here, in the database, and the client only ever holds an
opaque random token.

The table is resolved lazily so this module can be imported before ``create_app``
has registered the schema (tests, CLI, Alembic).
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

from flask import session
from sqlalchemy import delete, select, update

from common.connectDb import connectDb

dbsession, md, DBase = connectDb()

MAX_ATTEMPTS = 5


def _codes():
    return md.tables["one_time_code"]


def _session_key(kind):
    return f"{kind}_token"


def hash_code(code):
    return hashlib.sha256((code or "").strip().lower().encode("utf-8")).hexdigest()


def issue(kind, code, ttl, subject=None):
    """Store the hash of ``code`` and return the opaque token kept in the session."""
    table = _codes()
    dbsession.execute(delete(table).where(table.c.expires_at < datetime.now()))
    token = secrets.token_urlsafe(32)
    dbsession.execute(
        table.insert().values(
            token=token,
            kind=kind,
            code_hash=hash_code(code),
            subject=(subject or "")[:254],
            expires_at=datetime.now() + timedelta(seconds=ttl),
            attempts=0,
        )
    )
    dbsession.commit()
    session[_session_key(kind)] = token
    return token


def consume(kind, code, subject=None):
    """Verify a code and invalidate it. Succeeds at most once per issued code."""
    key = _session_key(kind)
    token = session.get(key)
    if not token or not code:
        return False
    table = _codes()
    row = dbsession.execute(select(table).where(table.c.token == token)).mappings().first()
    if row is None or row["kind"] != kind:
        session.pop(key, None)
        return False
    if row["expires_at"] < datetime.now() or row["attempts"] >= MAX_ATTEMPTS:
        dbsession.execute(delete(table).where(table.c.token == token))
        dbsession.commit()
        session.pop(key, None)
        return False
    if subject is not None and row["subject"] != subject[:254]:
        return False
    matched = hmac.compare_digest(row["code_hash"], hash_code(code))
    if matched:
        dbsession.execute(delete(table).where(table.c.token == token))
    else:
        dbsession.execute(
            update(table).where(table.c.token == token).values(attempts=row["attempts"] + 1)
        )
    dbsession.commit()
    if matched:
        session.pop(key, None)
    return matched


def revoke_subject(kind, subject):
    """Drop every outstanding code for a subject (used after a password reset)."""
    table = _codes()
    dbsession.execute(delete(table).where(table.c.kind == kind, table.c.subject == subject[:254]))
    dbsession.commit()
