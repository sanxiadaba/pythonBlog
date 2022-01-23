"""
文件说明：

本文件主要是对ueditor上传的实现
比如发送图片、获取内容等

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
from database.upload import Upload
from database.logs import Log

instanceUpload=Upload()
instanceLog=Log()

ueditor = Blueprint("ueditor", __name__)

# 上传文件的路径
imgSavePath = rootDir + "\\static\\img\\upload"


# 具体访问的接口
@ueditor.route("/uedit", methods=["GET", "POST"])
@logDanger
def uedit():
    param = request.args.get("action")
    if request.method == "GET" and param == "config":
        # return render_template("uecConfig.json")
        return returnUeConf(session.get("userid"))
    else:
        userid = session.get("userid")
        # 每个用户都有一个属于自己的文件夹，图片上传到这里
        myPictureName = "myPic_" + str(userid)
        myPicturePath = imgSavePath + "\\" + myPictureName
        # 检测前端ueditor发送的请求 不同的请求响应不同的状态
        if request.method == "POST" and request.args.get("action") == "uploadimage":
            if instanceUpload.checkLimitUpload() is True:
                result = {}
                # 每天有上传限制、上传次数用完的话前端会提示
                result["state"] = "每天上传次数已用完"
                info = f"userid为{userid}的用户因今天的上传次数用完故上传失败"
                instanceLog.insertDetail(credit=0, target=0, type="上传图片失败", info=info)
                listLogger(userid, info, 8)
                return jsonify(result)
            else:
                f = request.files["upfile"]  # 获取前端图片文件的数据
                filename = f.filename
                suffix = filename.split(".")[-1]  # 获取文章的后缀名（不包括.）
                newname = time.strftime("%Y%m%d_%H%M%S." + suffix)
                dirInDir(myPictureName, imgSavePath)
                f.save(myPicturePath + "\\" + newname)  # 保存图片
                # 对图片进行压缩 并覆盖原始文件
                source = dest = myPicturePath + "\\" + newname
                #  压缩图片
                compress_image(source, dest, 1200)
                instanceUpload.insertDetail(imgname=source)
                info = f"userid为{userid}的用户，上传了路径为" + source + "的图片"
                instanceLog.insertDetail(credit=0, target=0, type="上传图片", info=info)
                listLogger(userid, info, [8])
                result = {}
                # 返回成功的状态码
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
