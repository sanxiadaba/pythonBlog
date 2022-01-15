"""

文件说明

本文件主要关于管理员后台控制的页面

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/14
@gituhb: sanxiadaba/pythonBlog
"""

from flask import Blueprint, session, jsonify, render_template

from database.instanceDatabase import instanceArticle

adminManage = Blueprint("adminManage", __name__)


@adminManage.route("/zanding", methods=["GET"])
def baseManage():
    if session.get("role") != "admin":
        return render_template("userManage.html")
    else:
        return render_template("adminManage.html")


# 查看所有成员信息（用户数量、身份、qq等）

# 更改身份

# 查看成为编辑的申请

# 删除评论

# 隐藏文章（审核通过文章）

# 设置编辑推荐按文章

# 修改积分

# 移除用户（将用户不可登录）

# 修改栏目名称

# 所以文章数量

# 所有评论数量

# 全部的访问量

# 查看某一个用户的登录记录

# 网站参数的设置（评论、登录等）