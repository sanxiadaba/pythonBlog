"""

文件说明

本文件是测试、调试使用的

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/14
@gituhb: sanxiadaba/pythonBlog
"""

from flask import Blueprint, session

from database.instanceDatabase import *

test = Blueprint("test", __name__)


# 测试1 查看正常情况下sqlalchemy查询返回的数据是什么
@test.route("/test_1", methods=["GET"])
def test_1():
    # 返回的是一个由类组成的列表，元素里的元素可以用"."来查看
    a = instanceArticle.searchAllMyArticle()
    print(a)
    # [<Article 144>, <Article 145>, <Article 146>, <Article 147>, <Article 148>, <Article 149>, <Article 150>]
    for i in a:
        print(i.articleid)
    return "1"


# 测试2 查询一个表中的全部元素会怎样（在没有filter或filter的情况下）
# 事实证明返回的跟上一个测试的结果一样
@test.route("/test_2", methods=["GET"])
def test_2():
    # 返回的是一个由类组成的列表，元素里的元素可以用"."来查看
    a = instanceUser.searchAllUserInfo()
    print(a)
    return "2"


# 测试3 查看所有文章的回复数量以及阅读数量之和
@test.route("/test_3", methods=["GET"])
def test_3():
    a, b = instanceArticle.searchALLNumberOfComment()
    print(a, b)
    return "3"

# 测试四 查看当前nickname
@test.route("/test_4", methods=["GET"])
def test_4():
    nickname=session.get("nickname")
    print(nickname)
    return "3"
