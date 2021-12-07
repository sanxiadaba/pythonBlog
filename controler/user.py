from flask import Blueprint, make_response, session, request, redirect, url_for
from common.utility import ImageCode, gen_email_code, send_email
import re, hashlib

from database.credit import Credit
from database.users import Users

user = Blueprint("user", __name__)


# gofsuuskywdpdjec
@user.route("/vcode")
def vcode():
    image = ImageCode()
    code, bstring = image.get_code()
    response = make_response(bstring)
    response.headers['Content-Type'] = 'image/jpeg'
    session['vcode'] = code.lower()
    return response


@user.route("/ecode", methods=["POST"])
def ecode():
    email = request.form.get("email")
    # print(email)
    if not re.match(".+@.+\..+", email):
        # print(1)
        return "email-invailid"
    code = gen_email_code()
    try:
        send_email(email, code)
        # print("code=",code)
        session["ecode"] = code  # 将邮箱验证码保存在session中
        session.permanent = True
        # print("session[ecode]=",session.get("ecode"))
        # print("-----------")
        return "send-pass"
    except:
        return "send fail"

    # test
    # email=request.form.get("email")
    # code=gen_email_code()
    # session["ecode"] = code
    # print(code,email)
    # print(session.get("ecode"))
    # return "1"


@user.route("/user", methods=["POST"])
def register():
    # print("session[ecode]=", session.get("ecode"))
    user = Users()
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()
    ecode = request.form.get("ecode").strip()
    nickname = username.split("@")[0]

    # 校验邮箱验证码是否正确   # 或者也可以设置一个万能的验证码
    if ecode != session.get("ecode"):
        return "ecode-error"

    # 验证邮箱地址的正确性和密码的有效性
    elif not re.match(".+@.+\..+", username) or len(password) < 5:
        return "up-invalid"

    # 验证用户是否已经注册
    elif len(user.find_by_username(username)) > 0:
        return "user-repeated"

    else:
        # 实现注册功能
        password = hashlib.md5(password.encode()).hexdigest()
        try:
            result = user.do_register(username, password)
        except:
            return "reg-fail"
        session["islogin"] = "true"
        session["userid"] = result.userid
        session["nickname"] = nickname
        session["role"] = result.role
        # 更新积分表
        credit = Credit()
        credit.insert_detail(type="用户注册", target=0, credit=50)
        return "reg-pass"


@user.route("/login", methods=["POST"])
def login():
    # print("session[ecode]=", session.get("ecode"))
    user = Users()
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()
    vcode = request.form.get("logincode").lower().strip()
    nickname = username.split("@")[0]

    # 万能登陆验证码
    if vcode != session.get("vcode") and vcode != "zhimakaimen":
        return "vcode-error"

    else:
        # 实现登录功能
        password = hashlib.md5(password.encode()).hexdigest()
        result = user.find_by_username(username)
        if len(result) == 1 and result[0].password == password:
            session["islogin"] = "true"
            session["userid"] = result[0].userid
            session["nickname"] = nickname
            session["role"] = result[0].role
            # 更新积分表
            credit = Credit()
            credit.insert_detail(type="正常登录", target=0, credit=1)
            user.update_credit(1)
            response = make_response("login-pass")
            response.set_cookie("username", username, max_age=30 * 24 * 3600)
            response.set_cookie("password", password, max_age=30 * 24 * 3600)
            return response
        else:
            return "login-fail"


@user.route("/logout")
def logout():
    # 清空session 页面跳转
    session.clear()
    response = make_response("注销并重定向", 302)
    # response.headers["Location"]="/"  # 这样也行
    response.headers["Location"] = url_for("index.home")
    response.delete_cookie("username")
    response.set_cookie("password", max_age=0)  # 这是另一种写法
    return response
