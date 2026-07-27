from datetime import datetime, timedelta

from flask import request, session

from common.connectDb import connectDb
from constant import maxUploadPicNum

dbsession, md, DBase = connectDb()


class Upload(DBase):
    __table__ = md.tables["upload"]

    # Insert information about the uploaded image
    def insertDetail(self, imgname, info=None):
        userid = session.get("userid")
        now = datetime.now()
        uploadP = Upload(userid=userid, imgname=imgname, createtime=now,
                         ipaddr=request.remote_addr, info=info)

        dbsession.add(uploadP)
        dbsession.commit()

    # Determine if the number of user uploads exceeds the daily limit
    def checkLimitUpload(self):
        start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        result = dbsession.query(Upload).filter(Upload.userid == session.get("userid"),
                                                Upload.createtime.between(start, end),
                                                Upload.info != "Upload thumbnails").count()
        if result >= maxUploadPicNum:
            return True
        else:
            return False
