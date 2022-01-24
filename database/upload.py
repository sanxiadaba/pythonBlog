import time

from flask import session, request
from sqlalchemy import Table

from common.connectDb import connectDb
from constant import maxUploadPicNum

dbsession, md, DBase = connectDb()


class Upload(DBase):
    __table__ = Table("upload", md, autoload=True)

    # Insert information about the uploaded image
    def insertDetail(self, imgname, info=None):
        userid = session.get("userid")
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        uploadP = Upload(userid=userid, imgname=imgname, createtime=now,
                         ipaddr=request.remote_addr, info=info)

        dbsession.add(uploadP)
        dbsession.commit()

    # Determine if the number of user uploads exceeds the daily limit
    def checkLimitUpload(self):
        start = time.strftime("%Y-%m-%d 00:00:00")
        end = time.strftime("%Y-%m-%d 23:59:59")
        result = dbsession.query(Upload).filter(Upload.userid == session.get("userid"),
                                                Upload.createtime.between(start, end),
                                                Upload.info != "Upload thumbnails").count()
        if result >= maxUploadPicNum:
            return True
        else:
            return False
