"""
文件说明：

关于整个博客项目的许多配配置参数
每个参数都有注释说明

encoding: utf-8
@author: Zhang Jiajun
@contact: jz272381@gmail.com
@software: Pycharm
@time: 2022/1/12
@gituhb: sanxiadaba/pythonBlog
"""

from datetime import timedelta

"""这里填写mysql配置
若是远程 配置格式例如“root(远程主机用户名):root(mysql用户名)@***.**.**.***(ip地址):3306(端口号)” 
比如
config_mysql=mysql://root:root@120.28.243.198:3306(这个地址不存在，只是做一下事例)
"""
config_mysql = "root@localhost:3306"

# 设置所在数据库的名称(下面是我测试用的数据库的名称，具体项目需要更改)
databaseName = "myBlog"

# 设置端口号
portNum = 1234

# 是否已debug模式进行启动 (开启的话，在后端修改对应的代码后
# 服务器会自动重启，建议在正式项目中设置为false)
whetherDebug = True

# 设置session的过期时间  这里还可以设置weeks,months等
sessionExpirationTime = timedelta(days=30)

# 设置每次服务器重启后session是否失效,默认为false，即重启服务器后session仍然生效
sessionRestart = False

# 设置主页的分类名字，这里写五个，也可以添加
classification = ["Python技巧", "LeetCode刷题", "项目开发", "综合学习", "其它"]

# 发送注册邮箱的账户
emailAccount = "*******"

""" 注册邮箱的授权码(不是邮箱的登录密码)  #参考这个网站（https://www.ujcms.com/documentation/351.html）
现只支持qq邮箱的发送服务，而且注册时也最好使用qq邮箱注册（不便之处，敬请原谅）"""

emailAdmit = "*******"

# 是否使用github的第三方登录功能 (需要进行相关配置，详情见readme文档)
whetherUseGithubLogin = True

# 设置github第三方登录所需要的Client ID 与 Client secrets # 待开发
# GITHUB_CLIENT_ID = '*********'
# GITHUB_CLIENT_SECRET = '***********'

# 设置没人每天的最多评论次数
commentNum = 10

# 图片验证码是否支持大小写不区分（这里指的是登录用的图片验证码，不是注册账号时的文字验证码）
whetherDistinguishCapital = False

# 注册送的积分数量
regGiveCredit = 50

# 每天登录送的积分（已做过处理，每天只能领取一次登录积分奖励）
loginEvereDayCredit = 1

# 发表文章送的积分(这里没有对每天发送文章数量做出限制，所以请谨慎给editor身份)
postArticleCredit = 10

# 添加评论和回复评论每次积分的增加积分
replyAndAddCommentCredit = 2

# 作者设置文章收取积分，其他读者支付积分后作者的分成比例
rateCreditForArticle = 0.5

# 发布带积分文章可供选择的收取积分
creditListForReleaseArticle = [1, 2, 5, 10, 20, 50]

# 每页有几篇文章
howArticleInWeb = 10

# 每篇文章有几条评论(不算上回复评论的回复)
howCommentInArticle = 5

# 是否要首页的轮播图
whetherSaveShufflingFigure = True

# 轮播图对应的图片位置 注意要与下面图片链接个数保持一致
# 注意，这里要要是在/static/img/banner 底下的图片（下面只填写文件名）
shufflingFigurePicture = ["banner-1.jpg", "banner-2.jpg", "banner-3.jpg"]

# 点击轮播图对应图片的链接
shufflingFigureLink = ["https://github.com/sanxiadaba/pythonBlog", "https://github.com/sanxiadaba/pythonBlog",
                       "https://github.com/sanxiadaba/pythonBlog"]

# 首页左上角的logo地址(这里图片的位置放在/static/img/logo下面)
indexLogoPicture = "logo.png"

# logo对应的长和宽(数组形式)
indexLogoPictureSize = (60, 60)

# 首页最上面的两个词 和移动端左上角的字
indexAboveStr = ["欢迎来到我的博客", "好好学习", "天天向上"]

# 随机生成头像缩略图的数量（用户注册时随机生成一个缩略图，后期读者可以更改）
# 要确保/static/img/avatar 底下有相应数量的头像图片
thumbNailNum = 10

# 侧边栏三个栏位里的推荐条数
# 最新文章 最多阅读 特别推荐
recommendedNumOfSide = [9, 9, 9]

"""
下面是日志文件的相关设置
"""
# 压缩文件的格式
compressedFormat = "zip"

# 定期清理的时间  (可选的比如 "1 day" "1 week" "3 months"等 ) 注意时间的复数
clearLogTime = "1 month"

# 分割日志的大小（日志到一定体积后自动压缩，然后开始新的日志） 可选的参数有KB GM MB
logSize = "0.1 MB"

# 打印的loguru是否在控制台输出
whetherLogPrintInConsole = True

# 超过指定时间后验证码便会失效  # 单位秒
timeoutOfEcode = 120

# 设置每个用户、编辑每天最多投稿、发布文章的数量
maxUserPostArticleNum = 10
maxUserPostArticleNumOfEditor = 20

# 设置每天最多的修改文章次数
maxModifyArticleNum = 10

# 每个人每天最多上传图片的数量
maxUploadPicNum = 20

# 设置在管理文章的后台页面，没几个文章分页
everyPageInHou = 2
