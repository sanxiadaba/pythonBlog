from sqlalchemy import MetaData


def connect_db():
    from app import db
    dbsession = db.session
    DBase = db.Model
    metadata = MetaData(bind=db.engine)
    return dbsession, metadata, DBase