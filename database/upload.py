import time

from flask import session, request
from sqlalchemy import Table

from common.connect_db import connect_db
from constant import maxUploadPicNum

dbsession, md, DBase = connect_db()


class Upload(DBase):
    __table__ = Table("upload", md, autoload=True)

    # 插入上传图片的相关信息
    def insert_detail(self, imgname, info=None):
        userid = session.get("userid")
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        uploadP = Upload(userid=userid, imgname=imgname, createtime=now,
                         ipaddr=request.remote_addr, info=info)

        dbsession.add(uploadP)
        dbsession.commit()

    # 判断用户上传次数是否超过当日限制
    def checkLimitUpload(self):
        start = time.strftime("%Y-%m-%d 00:00:00")
        end = time.strftime("%Y-%m-%d 23:59:59")
        result = dbsession.query(Upload).filter(Upload.userid == session.get("userid"),
                                                Upload.createtime.between(start, end), Upload.info != "上传缩略图").count()
        if result >= maxUploadPicNum:
            return True
        else:
            return False
