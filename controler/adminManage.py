"""

File Description

This file is mainly about the administrator backend control page

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/14
@gituhb: sanxiadaba/pythonBlog
"""

from flask import Blueprint, session, render_template

adminManage = Blueprint("adminManage", __name__)


@adminManage.route("/adminManage", methods=["GET"])
def baseAdminManage():
    return render_template("adminManage.html")

