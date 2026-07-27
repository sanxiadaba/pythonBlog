import hashlib
import re
import time

from flask import Blueprint, make_response, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from common.auth import login_required, role_required
from common.myLog import avatarPath, dirInDir, ininUserDir, listLogger, logDanger
from common.utility import ImageCode, gen_email_code, send_email
from constant import (
    emailAccount,
    loginEvereDayCredit,
    md5Salt,
    regGiveCredit,
    timeoutOfEcode,
    whetherDistinguishCapital,
)
from database.credit import Credit
from database.logs import Log
from database.users import Users
from extensions import limiter

instanceCredit = Credit()
instanceLog = Log()
instanceUser = Users()
user = Blueprint("user", __name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _valid_password(password):
    return isinstance(password, str) and 8 <= len(password) <= 128


def _email_code_valid(email, code):
    issued_at = session.get("ecode_issued_at", 0)
    return (
        code
        and code == session.get("ecode")
        and email == session.get("ecode_email")
        and time.time() - issued_at <= timeoutOfEcode
    )


def _password_matches(user_record, raw_password):
    stored = user_record.password or ""
    try:
        if check_password_hash(stored, raw_password):
            return True
    except (ValueError, TypeError):
        pass
    legacy = hashlib.md5((raw_password + md5Salt).encode()).hexdigest()
    if stored == legacy:
        instanceUser.modifyUserPassword(user_record.userid, generate_password_hash(raw_password, method="scrypt"))
        return True
    return False


@user.get("/vcode")
@limiter.limit("30 per minute")
@logDanger
def vcode():
    code, image = ImageCode().get_code()
    session["vcode"] = code if whetherDistinguishCapital else code.lower()
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpeg"
    response.headers["Cache-Control"] = "no-store"
    return response


@user.post("/ecode")
@limiter.limit("3 per 10 minutes")
@logDanger
def ecode():
    email = (request.form.get("email") or "").strip().lower()
    try:
        purpose = int(request.form.get("n", "0"))
    except ValueError:
        return "email-invailid", 400
    if not _EMAIL_RE.fullmatch(email):
        return "email-invailid", 400
    code = gen_email_code()
    send_email(email, code, purpose)
    session.update(ecode=code, ecode_email=email, ecode_issued_at=time.time())
    session.permanent = True
    return "send-pass"


@user.post("/user")
@limiter.limit("5 per hour")
@logDanger
def register():
    username = (request.form.get("username") or "").strip().lower()
    raw_password = request.form.get("password") or ""
    code = (request.form.get("ecode") or "").strip()
    if not _EMAIL_RE.fullmatch(username) or not _valid_password(raw_password):
        return "up-invalid", 400
    if instanceUser.searchUserByUsername(username) is not None:
        return "user-repeated", 409
    if not _email_code_valid(username, code):
        return "ecode-error", 400

    result = instanceUser.doRegister(username, generate_password_hash(raw_password, method="scrypt"))
    session.clear()
    session.update(islogin="true", userid=result.userid, nickname=result.nickname, role=result.role)
    session.permanent = True
    info = f"userid is {result.userid}, nickname is {result.nickname} user registration success"
    instanceCredit.insertDetail(
        type="User Registration", target=0, credit=regGiveCredit, info=info, userid=result.userid
    )
    dirInDir(f"myPic_{result.userid}", avatarPath)
    ininUserDir(result.userid)
    listLogger(result.userid, info, [0])
    return "reg-pass"


@user.post("/resetUserPassword")
@limiter.limit("5 per hour")
@logDanger
def resetUserPassword():
    username = (request.form.get("username") or "").strip().lower()
    raw_password = request.form.get("password") or ""
    code = (request.form.get("ecode") or "").strip()
    record = instanceUser.searchUserByUsername(username)
    if not _EMAIL_RE.fullmatch(username) or not _valid_password(raw_password):
        return "up-invalid", 400
    if record is None:
        return "no-user", 404
    if not _email_code_valid(username, code):
        return "ecode-error", 400
    instanceUser.modifyUserPassword(record.userid, generate_password_hash(raw_password, method="scrypt"))
    session.pop("ecode", None)
    return "fi-pass"


@user.post("/login")
@limiter.limit("10 per minute")
@logDanger
def login():
    username = (request.form.get("username") or "").strip().lower()
    raw_password = request.form.get("password") or ""
    captcha = (request.form.get("logincode") or "").strip()
    if not whetherDistinguishCapital:
        captcha = captcha.lower()
    record = instanceUser.searchUserByUsername(username)
    if record is None:
        return "login-fail", 401
    if captcha != session.get("vcode"):
        return "vcode-error", 400
    if record.forbidLogin == 1:
        return "forbid", 403
    if not _password_matches(record, raw_password):
        return "login-fail", 401

    session.clear()
    session.update(islogin="true", userid=record.userid, nickname=record.nickname, role=record.role)
    session.permanent = True
    ininUserDir(record.userid)
    first_login = instanceCredit.whetherFirstLoginThisDay(userid=record.userid)
    if first_login:
        info = f"userid is {record.userid}, nickname is {record.nickname} daily login plus points successfully"
        instanceCredit.insertDetail(
            userid=record.userid,
            type="Daily login bonus points",
            credit=loginEvereDayCredit,
            target=0,
            info=info,
        )
        session["judgeLin"] = "1"
        return "add-credit"
    return "login-pass"


@user.post("/logout")
@login_required
@logDanger
def logout():
    session.clear()
    response = make_response("Logout and redirect", 302)
    response.headers["Location"] = url_for("index.home")
    response.delete_cookie("username")
    response.delete_cookie("password")
    return response


@user.get("/adminMail")
def adminMail():
    return str(emailAccount)


def _change_user(userid, action, description):
    target = instanceUser.searchUserByUserid(userid)
    if target is None:
        return "0", 404
    action(userid)
    info = f"Administrator {description} userid {userid} ({target.nickname})"
    instanceLog.insertDetail(type=description, target=userid, credit=0, info=info)
    return "1"


@user.post("/becomeEditor")
@role_required("admin")
@logDanger
def becomeEditor():
    return _change_user(int(request.form["userid"]), instanceUser.becomeEditor, "set to editor")


@user.post("/becomeUser")
@role_required("admin")
@logDanger
def becomeUser():
    return _change_user(int(request.form["userid"]), instanceUser.becomeUser, "set to user")


@user.post("/forbidLogin")
@role_required("admin")
@logDanger
def forbidLogin():
    return _change_user(int(request.form["userid"]), instanceUser.forbidUserLogin, "forbid login")


@user.post("/restoreLogin")
@role_required("admin")
@logDanger
def restoreLogin():
    return _change_user(int(request.form["userid"]), instanceUser.restoreLogin, "restore login")
