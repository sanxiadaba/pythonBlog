"""
File description.

This file is mainly an implementation of ueditor upload
such as sending images, getting content, etc.

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""

import os
import time

from flask import Blueprint, request, jsonify, session

from common.myLog import rootDir, dirInDir, logDanger, listLogger
from common.ueditorConf import returnUeConf
from common.utility import compress_image
from constant import blogLanguage
from database.logs import Log
from database.upload import Upload

instanceUpload = Upload()
instanceLog = Log()

ueditor = Blueprint("ueditor", __name__)

# Path to the uploaded file
imgSavePath = rootDir + "\\static\\img\\upload"


# Interface for specific access
@ueditor.route("/uedit", methods=["GET", "POST"])
@logDanger
def uedit():
    param = request.args.get("action")
    if request.method == "GET" and param == "config":
        # return render_template("uecConfig.json")
        return returnUeConf(session.get("userid"))
    else:
        userid = session.get("userid")
        # Each user has a folder of their own and pictures are uploaded here
        myPictureName = "myPic_" + str(userid)
        myPicturePath = imgSavePath + "\\" + myPictureName
        # Detection of requests sent by front-end ueditor Different requests respond to different states
        if request.method == "POST" and request.args.get("action") == "uploadimage":
            if instanceUpload.checkLimitUpload() is True:
                result = {}
                # There is a daily upload limit, and the front-end will prompt if the number of uploads is used up.
                if blogLanguage == "Chinese":
                    result["state"] = "今日上传次数已用完"
                else:
                    result["state"] = "Exceeding the number of times limit"
                info = f"The user with userid {userid} failed to upload because he ran out of uploads today."
                instanceLog.insertDetail(credit=0, target=0, type="Failed to upload image", info=info)
                listLogger(userid, info, 8)
                return jsonify(result)
            else:
                f = request.files["upfile"]  # Get data from front-end image files
                filename = f.filename
                suffix = filename.split(".")[-1]  # Get the article's suffix name (not including .)
                newname = time.strftime("%Y%m%d_%H%M%S." + suffix)
                dirInDir(myPictureName, imgSavePath)
                f.save(myPicturePath + "\\" + newname)  # Save image
                # Compress the image and overwrite the original file
                source = dest = myPicturePath + "\\" + newname
                #  Compressed images
                compress_image(source, dest, 1200)
                instanceUpload.insertDetail(imgname=source)
                info = f"The user with userid {userid} has uploaded the image with path " + source + ""
                instanceLog.insertDetail(credit=0, target=0, type="Upload images", info=info)
                listLogger(userid, info, [8])
                result = {}
                # Returns a success status code
                result["state"] = "SUCCESS"
                result["url"] = f"static/img/upload/{myPictureName}/{newname}"
                result['title'] = filename
                result["original"] = filename
                return jsonify(result)

        elif request.method == "GET" and param == "listimage":
            list = []
            filelist = os.listdir(myPicturePath)
            for filename in filelist:
                if filename.lower().endswith(".png") or filename.lower().endswith(".jpg") \
                        or filename.lower().endswith(".jpeg") or filename.lower().endswith(".gif") \
                        or filename.lower().endswith(".bmp"):
                    list.append({r"url": r"static/img/upload/%s/%s" % (myPictureName, filename)})
            result = {}
            result["state"] = "SUCCESS"
            result["list"] = list
            result["start"] = 0
            result["total"] = 50
            return jsonify(result)
