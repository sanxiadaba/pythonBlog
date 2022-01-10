from sqlalchemy import MetaData


# 这里是连接数据库的一些设置（基本上都是一些固定的东西）

def connect_db():
    from app import db
    dbsession = db.session
    DBase = db.Model
    metadata = MetaData(bind=db.engine)
    return dbsession, metadata, DBase
