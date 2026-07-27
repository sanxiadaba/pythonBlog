from functools import wraps

from flask import abort, redirect, request, session, url_for


def current_user_id():
    return session.get("userid")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user_id():
            if request.accept_mimetypes.best == "application/json" or request.method != "GET":
                abort(401)
            return redirect(url_for("index.home"))
        return view(*args, **kwargs)

    return wrapped


def role_required(*roles):
    allowed = set(roles)

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            userid = current_user_id()
            if not userid:
                abort(401)
            from database.users import Users

            user = Users().searchUserByUserid(userid)
            if user is None or user.role not in allowed or user.forbidLogin == 1:
                session.clear()
                abort(403)
            session["role"] = user.role
            return view(*args, **kwargs)

        return wrapped

    return decorator


def article_owner_or_admin(articleid):
    userid = current_user_id()
    if not userid:
        abort(401)
    from database.article import Article
    from database.users import Users

    owner_id = Article().searchUseridByArticleid(articleid)
    if owner_id is None:
        abort(404)
    user = Users().searchUserByUserid(userid)
    if user is None or (int(owner_id) != int(userid) and user.role != "admin"):
        abort(403)
