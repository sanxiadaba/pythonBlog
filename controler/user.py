"""
文件说明：

主要对用户的信息进行了管理
以及登录、登出、注册、找回密码、验证码等信息


encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""

import hashlib
import re
import time
import traceback

from flask import Blueprint, make_response, session, request, url_for

from common.myLog import ininUserDir, logDanger, listLogger, allLogger, dirInDir, avatarPath
from common.utility import ImageCode, gen_email_code, send_email
from common.utility import genearteMD5
from constant import whetherDistinguishCapital, regGiveCredit, loginEvereDayCredit, timeoutOfEcode, md5Salt
from database.credit import Credit
from database.logs import Log
from database.users import Users

instanceCredit = Credit()
instanceLog = Log()
instanceUser = Users()

user = Blueprint("user", __name__)
# Used to determine if the verification code exceeds the time limit
timeStart = 0


# Here the image captcha is generated and the content of the captcha is stored in the session
@user.route("/vcode", methods=["GET"])
@logDanger
def vcode():
    image = ImageCode()
    code, bstring = image.get_code()
    response = make_response(bstring)
    response.headers['Content-Type'] = 'image/jpeg'
    # Here is the case-insensitive handling of the CAPTCHA
    if whetherDistinguishCapital is False:
        session['vcode'] = code.lower()
    else:
        session['vcode'] = code
    return response


# Generate email verification code here
@user.route("/ecode", methods=["POST"])
@logDanger
def ecode():
    global timeStart
    timeStart = time.time()
    email = request.form.get("email")
    # Convert to numeric type
    n = int(request.form.get("n"))
    if not re.match(".+@.+\..+", email):
        return "email-invailid"
    code = gen_email_code()
    try:
        send_email(email, code, n)
        session["ecode"] = code  # Save email verification code in session
        session.permanent = True
        return "send-pass"
    except:
        return "send fail"


# Interface for user registration access
@user.route("/user", methods=["POST"])
@logDanger
def register():
    global timeStart
    username = request.form.get("username").strip()
    password = request.form.get("password").strip() + md5Salt
    ecode = request.form.get("ecode").strip()
    nickname = username.split("@")[0]
    # Verify the correctness of the email address and the validity of the password
    if not re.match(".+@.+\..+", username) or len(password) < 5:
        return "up-invalid"

    if len(instanceUser.searchUserByUsername(username)) > 0:
        return "user-repeated"

    # Check if the email verification code is correct #or you can also set a universal verification code
    if ecode != session.get("ecode"):
        return "ecode-error"

    else:
        # Captcha will expire if the time exceeds
        if time.time() - timeStart > timeoutOfEcode:
            session["ecode"] = None
            return "ecode-timeout"
        # Implement the registration function to convert the password to md5 encryption under
        password = genearteMD5(password)
        try:
            result = instanceUser.doRegister(username, password)
        except:
            return "reg-fail"
        session["islogin"] = "true"
        session["userid"] = result.userid
        session["nickname"] = nickname
        session["role"] = result.role
        userid = session.get("userid")
        # Update the points table Every new user is given points if they register
        info = f"userid is {userid}, nickname is {nickname} user registration success"
        instanceCredit.insertDetail(type="User Registration", target=0, credit=regGiveCredit, info=info, userid=userid)
        listLogger(userid, info, [0])
        dirInDir(f"myPic_{userid}", avatarPath)
        ininUserDir()
        return "reg-pass"


# Module for password retrieval
@user.route("/resetUserPassword", methods=["POST"])
@logDanger
def resetUserPassword():
    username = request.form.get("username").strip()
    password = request.form.get("password").strip() + md5Salt
    ecode = request.form.get("ecode").strip()
    # First check whether the email account and password match the format
    if not re.match(".+@.+\..+", username) or len(password) < 5:
        return "up-invalid"

    # Check if this user is available
    if instanceUser.searchUserByUsername(username) is None:
        return "no-user"

    # Query userid according to play complete name
    userid = instanceUser.findUseridByUsername(username)
    userNickname = instanceUser.searchNicknameByUserid(userid)[0]

    # Verify that the email verification code is correct
    if ecode != session.get("ecode"):
        info = f"The user with userid {userid} and nickname {userNickname} tried to retrieve the password, but the email verification code was incorrectly entered."
        instanceLog.insertDetail(userid=userid, type="Mailbox verification code error", credit=0, target=0)
        listLogger(userid, info, [0])
        return "ecode-error"

    else:
        # Set the expiration time of the verification code
        if time.time() - timeStart > timeoutOfEcode:
            session["ecode"] = None
            info = f"The user with userid {userid} and nickname {userNickname} tried to retrieve the password, but the email verification code expired."
            instanceLog.insertDetail(userid=userid, type="Captcha Expired", credit=0, target=0)
            listLogger(userid, info, [0])
            return "ecode-timeout"
        userid = instanceUser.findUseridByUsername(username)
        # Convert password to md5 encryption under
        try:

            instanceUser.modifyUserPassword(userid, password)
            info = f"userid is {userid},nickname is {userNickname} reset password successfully by email verification code"
            instanceLog.insertDetail(userid=userid, type="Reset password", credit=0, target=0)
            listLogger(userid, info, [0])
        except:
            e = traceback.format_exc()
            allLogger(0, e)
            return "fi-fail"
        return "fi-pass"


# Module to implement login
@user.route("/login", methods=["POST"])
@logDanger
def login():
    username = request.form.get("username").strip()
    password = request.form.get("password").strip() + md5Salt
    vcode = request.form.get("logincode").lower().strip()
    # First determine if the account exists
    userid = instanceUser.findUseridByUsername(username)

    if userid is None:
        allLogger(0, "User does not exist")
        return "login-fail"
    nickname = instanceUser.searchNicknameByUserid(userid)[0]
    # This is the time to judge the directory just in case
    ininUserDir(userid=userid)
    # Re-verify that the verification code is correct
    #  Image Verification Code
    if vcode != session.get("vcode"):
        info = f"userid is {userid}, nickname is {nickname}, during the login process to check the image verification code input error"
        instanceLog.insertDetail(userid=userid, type="Login image verification code error", credit=0, target=0,
                                 info=info)
        listLogger(userid, info, [0])
        return "vcode-error"
    else:
        # Implementing the login function
        password = hashlib.md5(password.encode()).hexdigest()
        result = instanceUser.searchUserByUsername(username)
        if len(result) == 1 and result[0].password == password:
            session["islogin"] = "true"
            session["userid"] = result[0].userid
            session["nickname"] = nickname
            session["role"] = result[0].role
            # Add a record to the log table
            # If you have already received login credits
            # Determine if you have already logged in today (only the first login of each day will send points)
            whetherGetLoginCredit = instanceCredit.whetherFirstLoginThisDay(userid=userid)
            if whetherGetLoginCredit is False:
                response = make_response("login-pass")
            else:
                response = make_response("add-credit")
            #   Adding a record Setting cookies by the way
            response.set_cookie("username", username, max_age=30 * 24 * 3600)
            response.set_cookie("password", password, max_age=30 * 24 * 3600)
            if whetherGetLoginCredit is False:
                # Cannot receive login bonus
                info = f"userid is {userid}, nickname is {nickname}, but you have already received the daily login bonus"
                instanceLog.insertDetail(userid=userid, type="Successful login", credit=0, target=0,
                                         info=info)
                listLogger(userid, info, [0])
            else:
                # Receive daily login bonus
                info = f"userid is {userid}, nickname is {nickname} daily login plus points successfully"
                instanceCredit.insertDetail(userid=userid, type="Daily login bonus points", credit=loginEvereDayCredit,
                                            target=0,
                                            info=info)
                listLogger(userid, info, [0])
            return response
        else:
            # Record the login failure as well.
            info = f"userid is {userid}, nickname is {nickname} login failed, failure reason: login password error"
            instanceLog.insertDetail(userid=userid, type="Password error", credit=0, target=0, info=info)
            listLogger(userid, info, [0])
            return "login-fail"


# Logout settings
@user.route("/logout", methods=["POST", "GET"])
@logDanger
def logout():
    # Empty session page jump
    userid = session.get('userid')
    info = f"The user whose userid is {userid} and whose nickname is {session.get('nickname')} is logged out of the account"
    instanceLog.insertDetail(userid=userid, type="Logout page", credit=0, target=0, info=info)
    listLogger(userid, info, [0])
    session.clear()
    response = make_response("Logout and redirect", 302)
    response.headers["Location"] = url_for("index.home")
    response.delete_cookie("username")
    # Disable cookies
    response.set_cookie("password", max_age=0)  # This is another way of writing
    return response
