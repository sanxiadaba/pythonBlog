import random, string
import time
from datetime import datetime
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
from constant import emailPasswod,emailAccount,portNum
from hashlib import md5


class ImageCode:
    #  生成随机字符串
    def gen_text(self):
        list = random.sample(string.ascii_letters + string.digits, 4)
        return "".join(list)

    # 生成随机颜色
    def rand_color(self):
        red = random.randint(32, 200)
        green = random.randint(22, 255)
        blue = random.randint(0, 200)
        return red, green, blue

    # 画干扰线
    def draw_line(self, draw, num, width, height):
        for num in range(num):
            x1 = random.randint(0, width / 2)
            y1 = random.randint(0, height / 2)
            x2 = random.randint(0, width)
            y2 = random.randint(height / 2, height)
            draw.line(((x1, y1), (x2, y2)), fill="black", width=2)

    # 绘制验证码图片
    def draw_verify_code(self):
        code = self.gen_text()
        width, height = 120, 50  # 设置图片大小
        # 创建图片对象，并设置背景为白色
        im = Image.new("RGB", (width, height), "white")
        # 使用何种字体以及字体大小
        font = ImageFont.truetype(font="arial.ttf", size=40)
        draw = ImageDraw.Draw(im)  # 新建生成对象
        # 绘制字符串
        for i in range(4):
            draw.text((5 + random.randint(-3, 3) + 23 * i, 5 + random.randint(-3, 3)), text=code[i],
                      fill=self.rand_color(), font=font)
        # 绘制干扰线
        self.draw_line(draw, 2, width, height)
        # im.show()
        return im, code

    # 获取图片与验证码
    def get_code(self):
        img, code = self.draw_verify_code()
        buf = BytesIO()
        img.save(buf, "jpeg")
        bstring = buf.getvalue()
        return code, bstring





def send_email(receiver, ecode):
    sender = "2190165626@qq.com"
    # 定义发送文件的内容
    content = f"<br/>欢迎注册博客，你的邮箱验证码为：<span style='color:red;font-size:20px;'>{ecode}</span>,请复制到注册窗口完成注册，感谢你的支持。<br/>"
    message = MIMEText(content, "html", "utf-8")
    # 指定邮件标题
    message["Subject"] = Header("博客验证码为", "utf-8")
    message["From"] = Header(f"Blog <{emailAccount}>", 'utf-8')  # 指定发件人信息
    message["To"] = Header(receiver, 'utf-8')  # 指定收件人邮箱地址
    message['Date'] = Header(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             'utf-8')  # 时间可以这么获取：datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    smtpObj = SMTP_SSL("smtp.qq.com", 465)
    smtpObj.login(user=emailAccount, password=emailPasswod)
    smtpObj.sendmail(sender, receiver, str(message))
    smtpObj.quit()


def gen_email_code():
    list = random.sample(string.ascii_letters + string.digits, 6)
    return "".join(list)


# SQLALchemy 连接查询的两张表转化为 [(),()]
def model_join_list(result):
    list = []
    for obj1, obj2 in result:
        dict = {}
        for k1, v1 in obj1.__dict__.items():
            if not k1.startswith("_sa_instance_state"):
                if not k1 in dict:
                    dict[k1] = v1

        for k2, v2 in obj2.__dict__.items():
            if not k2.startswith("_sa_instance_state"):
                if not k2 in dict:
                    dict[k2] = v2
        list.append(dict)
    return list


# 单个模型类转化为python list数据
def model_list(result):
    list = []
    for row in result:
        dict = {}
        for k, v in row.__dict__.items():
            if not k.startswith("_sa_instance_state"):
                dict[k] = v
        list.append(dict)
    return list


# 压缩图片
def compress_image(source, dest, width):
    from PIL import Image
    im = Image.open(source)
    x, y = im.size
    if x > width:
        ys = int(y * width / x)
        xs = width

        temp = im.resize((xs, ys), Image.ANTIALIAS)
        temp.save(dest, quality=80)
    else:
        im.save(dest, quality=80)


# 解析文章中图片下载地址
def parser_image_url(content):
    import re
    temp_list = re.findall('<img src="(.+?)"', content)
    url_list = []
    for url in temp_list:
        # 如果图片为gif就不做任何处理
        if url.lower().endswith(".gif"):
            continue
        url_list.append(url)
    return url_list


# 下载远程图片到临时目录中
def download_image(url, dest):
    import requests
    response = requests.get(url)
    with open(file=dest, mode="wb") as file:
        file.write(response.content)


# 解析列表中的图片url并生成缩略图
def generate_thumb(url_list):
    for url in url_list:
        if url.startswith(f"http://127.0.0.1:{portNum}/static/img/upload/"):
            filename = url.split("/")[-1]
            compress_image("./static/img/upload/" + filename, "./static/img/thumb/" + filename, 400)
            return filename

    # 如果在内容中没有找到本地图片，需要将网络图片下载到本地再处理
    # 直接将第一张图片作为缩略图，并生成基于时间戳的标准文件名
    url = url_list[0]
    filename = url.split("/")[-1]
    suffix = filename.split(".")[-1]  # 取得文件的后缀名
    thumbname = time.strftime("%Y%m%d_%H%M%S." + suffix)
    download_image(url, "./static/img/download/" + thumbname)
    compress_image("./static/img/download/" + thumbname, "./static/img/thumb/" + thumbname, 400)
    return thumbname

# 设置获取时间戳的函数
def getDatatimeStr():
    return datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

# 生成MD5
def genearteMD5(strlin):
    strlin=str(strlin)
    # 创建md5对象
    hl = md5()
    # Tips
    # 此处必须声明encode
    # 否则报错为：hl.update(str)    Unicode-objects must be encoded before hashing
    hl.update(strlin.encode(encoding='utf-8'))
    return hl.hexdigest()

