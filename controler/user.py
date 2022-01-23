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
from constant import whetherDistinguishCapital, regGiveCredit, loginEvereDayCredit, timeoutOfEcode
from database.credit import Credit
from database.logs import Log
from database.users import Users
instanceCredit=Credit()
instanceLog=Log()
instanceUser=Users()

user = Blueprint("user", __name__)
# 用来判断验证码是否超过时间限制
timeStart = 0


# 这里生成图片验证码 验证码的内容会储存在session里
@user.route("/vcode", methods=["GET"])
@logDanger
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


# 这里生成邮件验证码
@user.route("/ecode", methods=["POST"])
@logDanger
def ecode():
    global timeStart
    timeStart = time.time()
    email = request.form.get("email")
    # 转换下数字类型
    n = int(request.form.get("n"))
    if not re.match(".+@.+\..+", email):
        return "email-invailid"
    code = gen_email_code()
    try:
        send_email(email, code, n)
        session["ecode"] = code  # 将邮箱验证码保存在session中
        session.permanent = True
        return "send-pass"
    except:
        return "send fail"


# 用户注册访问的接口
@user.route("/user", methods=["POST"])
@logDanger
def register():
    global timeStart
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()
    ecode = request.form.get("ecode").strip()
    nickname = username.split("@")[0]
    # 验证邮箱地址的正确性和密码的有效性
    if not re.match(".+@.+\..+", username) or len(password) < 5:
        return "up-invalid"

    if len(instanceUser.searchUserByUsername(username)) > 0:
        return "user-repeated"

    # 校验邮箱验证码是否正确   #或者也可以设置一个万能的验证码
    if ecode != session.get("ecode"):
        return "ecode-error"

    else:
        # 验证码时间超过的话就过期了
        if time.time() - timeStart > timeoutOfEcode:
            session["ecode"] = None
            return "ecode-timeout"
        # 实现注册功能 将密码转换为md5加密下
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
        # 更新积分表 每个新用户注册的话是送积分的
        info = f"userid为{userid},昵称为{nickname}的用户注册成功"
        instanceCredit.insertDetail(type="用户注册", target=0, credit=regGiveCredit, info=info, userid=userid)
        listLogger(userid, info, [0])
        dirInDir(f"myPic_{userid}", avatarPath)
        ininUserDir()
        return "reg-pass"


# 找回密码的模块
@user.route("/resetUserPassword", methods=["POST"])
@logDanger
def resetUserPassword():
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()
    ecode = request.form.get("ecode").strip()
    # 先检测邮箱账户、密码是否符合格式
    if not re.match(".+@.+\..+", username) or len(password) < 5:
        return "up-invalid"

    # 检查是否有这个用户
    if instanceUser.searchUserByUsername(username) is None:
        return "no-user"

    # 根据玩完整名查询userid
    userid = instanceUser.findUseridByUsername(username)
    userNickname = instanceUser.searchNicknameByUserid(userid)[0]

    # 校验邮箱验证码是否正确
    if ecode != session.get("ecode"):
        info = f"userid为{userid},昵称为{userNickname}的用户尝试找回密码，但邮箱验证码输入错误"
        instanceLog.insertDetail(userid=userid, type="邮箱验证码错误", credit=0, target=0)
        listLogger(userid, info, [0])
        return "ecode-error"

    else:
        # 设置验证码的失效时间
        if time.time() - timeStart > timeoutOfEcode:
            session["ecode"] = None
            info = f"userid为{userid},昵称为{userNickname}的用户尝试找回密码，但邮箱验证码过期"
            instanceLog.insertDetail(userid=userid, type="验证码过期", credit=0, target=0)
            listLogger(userid, info, [0])
            return "ecode-timeout"
        userid = instanceUser.findUseridByUsername(username)
        # 将密码转换为md5加密下
        try:
            instanceUser.modifyUserPassword(userid, password)
            info = f"userid为{userid},昵称为{userNickname}通过邮箱验证码成功重设密码"
            instanceLog.insertDetail(userid=userid, type="重设密码", credit=0, target=0)
            listLogger(userid, info, [0])
        except:
            e = traceback.format_exc()
            allLogger(0, e)
            return "fi-fail"
        return "fi-pass"


# 实现登录的模块
@user.route("/login", methods=["POST"])
@logDanger
def login():
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()
    vcode = request.form.get("logincode").lower().strip()
    # 先判断账户是否存在
    userid = instanceUser.findUseridByUsername(username)

    if userid is None:
        allLogger(0, "用户不存在")
        return "login-fail"
    nickname = instanceUser.searchNicknameByUserid(userid)[0]
    # 这个时候就要判断目录了以防万一
    ininUserDir(userid=userid)
    # 再验证验证码对不对
    #  图片验证码
    if vcode != session.get("vcode"):
        info = f"userid为{userid},昵称为{nickname}登录过程中验图片验证码输入错误"
        instanceLog.insertDetail(userid=userid, type="登录图片验证码错误", credit=0, target=0, info=info)
        listLogger(userid, info, [0])
        return "vcode-error"
    else:
        # 实现登录功能
        password = hashlib.md5(password.encode()).hexdigest()
        result = instanceUser.searchUserByUsername(username)
        if len(result) == 1 and result[0].password == password:
            session["islogin"] = "true"
            session["userid"] = result[0].userid
            session["nickname"] = nickname
            session["role"] = result[0].role
            # 向log表中添加记录
            # 已经领过登录积分的情况下
            # 判断今天是否已经登陆过了（每天的首次登录才会送积分）
            whetherGetLoginCredit = instanceCredit.whetherFirstLoginThisDay(userid=userid)
            if whetherGetLoginCredit is False:
                response = make_response("login-pass")
            else:
                response = make_response("add-credit")
            #   加入记录 顺便设置cookies
            response.set_cookie("username", username, max_age=30 * 24 * 3600)
            response.set_cookie("password", password, max_age=30 * 24 * 3600)
            if whetherGetLoginCredit is False:
                # 不能领取登陆奖励
                info = f"userid为{userid},昵称为{nickname}登录成功，但已领取过每天的登录奖励"
                instanceLog.insertDetail(userid=userid, type="成功登录", credit=0, target=0,
                                         info=info)
                listLogger(userid, info, [0])
            else:
                # 领取每天的登陆奖励
                info = f"userid为{userid},昵称为{nickname}每日登录加分成功"
                instanceCredit.insertDetail(userid=userid, type="每日登录加分", credit=loginEvereDayCredit, target=0,
                                            info=info)
                listLogger(userid, info, [0])
            return response
        else:
            # 记录下登录失败的话也进行记录
            info = f"userid为{userid},昵称为{nickname}登录失败,失败原因:登录密码错误"
            instanceLog.insertDetail(userid=userid, type="登录成功", credit=0, target=0, info=info)
            listLogger(userid, info, [0])
            return "login-fail"


# 登出的设置
@user.route("/logout")
@logDanger
def logout():
    # 清空session 页面跳转
    userid = session.get('userid')
    info = f"userid为{userid} 昵称为{session.get('nickname')}的用户登出账户"
    instanceLog.insertDetail(userid=userid, type="登出页面", credit=0, target=0, info=info)
    listLogger(userid, info, [0])
    session.clear()
    response = make_response("注销并重定向", 302)
    response.headers["Location"] = url_for("index.home")
    response.delete_cookie("username")
    # 将cookies失效
    response.set_cookie("password", max_age=0)  # 这是另一种写法
    return response
