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
import secrets

from flask import Blueprint, jsonify, request, session
from flask_wtf.csrf import ValidationError, validate_csrf

from common.auth import login_required
from common.myLog import dirInDir, listLogger, logDanger, rootDir
from common.ueditorConf import returnUeConf
from common.utility import save_image_bytes
from constant import blogLanguage
from database.logs import Log
from database.upload import Upload
from extensions import csrf

instanceUpload = Upload()
instanceLog = Log()

ueditor = Blueprint("ueditor", __name__)


@ueditor.before_request
@login_required
def require_login():
    """Uploaded media is always scoped to an authenticated user."""

# Path to the uploaded file
imgSavePath = rootDir + "\\static\\img\\upload"


# Interface for specific access
@ueditor.route("/uedit", methods=["GET", "POST"])
@csrf.exempt
@logDanger
def uedit():
    if request.method == "POST":
        try:
            validate_csrf(request.args.get("csrf_token"))
        except ValidationError:
            return jsonify(state="Invalid CSRF token"), 400
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
                f = request.files.get("upfile")
                if f is None:
                    return jsonify(state="Missing upload"), 400
                filename = f.filename
                newname = f"{secrets.token_hex(16)}.jpg"
                dirInDir(myPictureName, imgSavePath)
                source = myPicturePath + "\\" + newname
                try:
                    save_image_bytes(f.stream.read(5 * 1024 * 1024 + 1), source)
                except ValueError as exc:
                    return jsonify(state=str(exc)), 400
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
            dirInDir(myPictureName, imgSavePath)
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
