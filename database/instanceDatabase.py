#  本包是对数据库的实例化，以后直接引用库然后调用方法就行

from database.article import Article
from database.comment import Comment
from database.favorite import Favorite
from database.logs import Log
from database.users import Users
from database.credit import Credit
from database.upload import Upload
from database.articleLog import ArticleLog

instanceUser = Users()
instanceArticle = Article()
instanceLog = Log()
instanceComment = Comment()
instanceFavorite = Favorite()
instanceCredit=Credit()
instanceUpload=Upload()
instanceArticleLog=ArticleLog()
