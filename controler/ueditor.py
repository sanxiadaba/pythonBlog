import os
import time

from flask import Blueprint, render_template, session, request, jsonify

from common.utility import compress_image

ueditor = Blueprint("ueditor", __name__)


@ueditor.route("/uedit", methods=["GET", "POST"])
def uedit():
    param = request.args.get("action")
    if request.method == "GET" and param == "config":
        return render_template("uecConfig.json")
    elif request.method == "POST" and request.args.get("action") == "uploadimage":
        f = request.files["upfile"]  # 获取前端图片文件的数据
        filename = f.filename

        suffix = filename.split(".")[-1]  # 获取文章的后缀名（不包括.）
        newname = time.strftime("%Y%m%d_%H%M%S." + suffix)
        f.save("./static/upload/" + newname)  # 保存图片

        # 对图片进行压缩 并覆盖原始文件
        source = dest = "./static/upload/" + newname
        compress_image(source, dest, 1200)

        result = {}
        result["state"] = "SUCCESS"
        result["url"] = f"static/upload/{newname}"
        result['title'] = filename
        result["original"] = filename

        return jsonify(result)
    elif request.method == "GET" and param == "listimage":
        list = []
        filelist = os.listdir(r"static/upload")
        # print("filelist",filelist)
        for filename in filelist:
            # print("filename",filename.lower())
            # [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
            if filename.lower().endswith(".png") or filename.lower().endswith(".jpg") \
                    or filename.lower().endswith(".jpeg") or filename.lower().endswith(".gif") \
                    or filename.lower().endswith(".bmp"):
                list.append({r"url": r"static/upload/%s" % filename})
                # print("list",list)
        result = {}
        result["state"] = "SUCCESS"
        result["list"] = list
        result["start"] = 0
        result["total"] = 50
        # print("result",result)
        return jsonify(result)
