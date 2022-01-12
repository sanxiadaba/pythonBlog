# 这里对ueditor上传图片进行了相关设置

import os
import time
from common.myLog import rootDir,dirInDir,logDanger,allLogger,listLogger
from flask import Blueprint, render_template, request, jsonify,session
from common.ueditorConf import returnUeConf
from common.utility import compress_image
from database.instanceDatabase import instanceUpload,instanceLog

ueditor = Blueprint("ueditor", __name__)

imgSavePath=rootDir+"/static/img/upload"


@ueditor.route("/uedit", methods=["GET", "POST"])
@logDanger
def uedit():
    param = request.args.get("action")
    if request.method == "GET" and param == "config":
        # return render_template("uecConfig.json")
        return returnUeConf(session.get("userid"))
    else:
        userid = session.get("userid")
        myPictureName = "myPic_" + str(userid)
        myPicturePath = imgSavePath + "\\" + myPictureName

        if request.method == "POST" and request.args.get("action") == "uploadimage":
            if instanceUpload.checkLimitUpload() is True:
                result = {}
                result["state"] = "每天上传次数已用完"
                info=f"userid为{userid}的用户因今天的上传次数用完故上传失败"
                instanceLog.insert_detail(credit=0, target=0, type="上传图片失败", info=info)
                listLogger(userid,info,8)
                return  jsonify(result)
            else:
                f = request.files["upfile"]  # 获取前端图片文件的数据
                filename = f.filename
                suffix = filename.split(".")[-1]  # 获取文章的后缀名（不包括.）
                newname = time.strftime("%Y%m%d_%H%M%S." + suffix)
                dirInDir(myPictureName, imgSavePath)
                print(myPicturePath+"/" + newname)
                f.save(myPicturePath+"/" + newname)  # 保存图片
                # 对图片进行压缩 并覆盖原始文件
                source = dest = myPicturePath+"/" + newname
                compress_image(source, dest, 1200)
                instanceUpload.insert_detail(imgname=myPictureName+"\\" + newname)
                info=f"userid为{userid}的用户，上传了名称为"+myPictureName+"\\" + newname+"的图片"
                instanceLog.insert_detail(credit=0,target=0,type="上传图片",info=info)
                listLogger(userid,info,[8])
                result = {}
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
                    list.append({r"url": r"static/img/upload/%s/%s" % (myPictureName,filename)})
            result = {}
            result["state"] = "SUCCESS"
            result["list"] = list
            result["start"] = 0
            result["total"] = 50
            return jsonify(result)
