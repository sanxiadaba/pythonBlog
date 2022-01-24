"""
File description.

Here are some settings for connecting to the sqlalchemy database (all are fixed in some way to write)

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""

from sqlalchemy import MetaData


def connectDb():
    from app import db
    dbsession = db.session
    DBase = db.Model
    metadata = MetaData(bind=db.engine)
    return dbsession, metadata, DBase
