"""
文件说明：

这里是连接sqlalchemy数据库的一些设置（都是一些固定的写法）

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""

from sqlalchemy import MetaData

def connect_db():
    from app import db
    dbsession = db.session
    DBase = db.Model
    metadata = MetaData(bind=db.engine)
    return dbsession, metadata, DBase
