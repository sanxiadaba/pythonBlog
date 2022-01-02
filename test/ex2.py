from database.instanceDatabase import instanceCredit,instanceComment
from app import app
with app.app_context():
    print(instanceComment.check_limit_per_day())
# print(instanceCredit.check_limit_login_per_day())