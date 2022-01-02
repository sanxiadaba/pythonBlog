from datetime import timedelta


# 这里填写mysql配置
# 若是远程 配置格式例如“root(远程主机用户名):root(mysql用户名)@***.**.**.***(ip地址):3306(端口号)”

config_mysql = "root@localhost:3306"

# 设置端口号
portNum=1234

# 设置session的过期时间  这里还可以设置weeks,months等
sessionExpirationTime=timedelta(days=30)

# 设置每次服务器重启后session是否失效,默认为false，即重启服务器后session仍然生效
sessionRestart=False

# 设置主页的分类名字，这里写五个，也可以添加
classification=["Python技巧","LeetCode刷题","项目开发","综合学习","其它"]

# 发送注册邮箱的账户
emailAccount="2190165626@qq.com"

# 注册邮箱的授权码(不是邮箱的登陆密码)  #参考这个网站（https://www.ujcms.com/documentation/351.html）
# 现只支持qq邮箱的发送服务，而且注册时也最好使用qq邮箱注册（不便之处，敬请原谅）
emailPasswod="gofsuuskywdpdjec"

# 设置没人每天的最多评论次数
commentNum=5