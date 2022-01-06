from flask import Blueprint, make_response, session, request ,url_for
from common.utility import ImageCode, gen_email_code, send_email
import re, hashlib
from common.utility import genearteMD5
from database.instanceDatabase import instanceCredit,instanceUser
from constant import whetherDistinguishCapital,regGiveCredit,loginEvereDayCredit

user = Blueprint("user", __name__)


@user.route("/vcode")
def vcode():
    image = ImageCode()
    code, bstring = image.get_code()
    response = make_response(bstring)
    response.headers['Content-Type'] = 'image/jpeg'
    # 这里对验证码进行不区分大小写处理
    if whetherDistinguishCapital is False:
        session['vcode'] = code.lower()
    else:
        session['vcode'] = code
    return response


@user.route("/ecode", methods=["POST"])
def ecode():
    email = request.form.get("email")
    if not re.match(".+@.+\..+", email):
        return "email-invailid"
    code = gen_email_code()
    try:
        send_email(email, code)
        session["ecode"] = code  # 将邮箱验证码保存在session中
        session.permanent = True
        return "send-pass"
    except:
        return "send fail"



@user.route("/user", methods=["POST"])
def register():
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()
    ecode = request.form.get("ecode").strip()
    nickname = username.split("@")[0]

    # 校验邮箱验证码是否正确   #或者也可以设置一个万能的验证码
    if ecode != session.get("ecode"):
        return "ecode-error"

    # 验证邮箱地址的正确性和密码的有效性
    elif not re.match(".+@.+\..+", username) or len(password) < 5:
        return "up-invalid"

    # 验证用户是否已经注册
    elif len(instanceUser.find_by_username(username)) > 0:
        return "user-repeated"

    else:
        # 实现注册功能 将密码转换为md5加密下
        password = genearteMD5(password)
        try:
            result = instanceUser.do_register(username, password)
        except:
            return "reg-fail"
        session["islogin"] = "true"
        session["userid"] = result.userid
        session["nickname"] = nickname
        session["role"] = result.role
        # 更新积分表
        instanceCredit.insert_detail(type="用户注册", target=0, credit=regGiveCredit)
        return "reg-pass"


@user.route("/login", methods=["POST"])
def login():
    # 判断是否加一
    #  如果今天的登录分没有领过
    whetherAddCredit=1 if instanceCredit.check_limit_login_per_day() is False else 0
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()
    vcode = request.form.get("logincode").lower().strip()
    nickname = username.split("@")[0]
    # 万能登陆验证码
    if vcode != session.get("vcode"):
        return "vcode-error"
    else:
        # 实现登录功能
        password = hashlib.md5(password.encode()).hexdigest()
        result = instanceUser.find_by_username(username)
        if len(result) == 1 and result[0].password == password:
            session["islogin"] = "true"
            session["userid"] = result[0].userid
            session["nickname"] = nickname
            session["role"] = result[0].role
            # 更新积分表
            if whetherAddCredit==0:
                instanceCredit.insert_detail(type="正常登录", target=0, credit=loginEvereDayCredit)
                response = make_response("login-pass")
            else:
                response = make_response("add-credit")
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
    response.headers["Location"] = url_for("index.home")
    response.delete_cookie("username")
    response.set_cookie("password", max_age=0)  # 这是另一种写法
    return response
