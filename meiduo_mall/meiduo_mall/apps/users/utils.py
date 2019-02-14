from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt token扩展登录视图响应数据的函数
    """
    return {
        'user_id':user.id,
        'username':user.username,
        'token': token
    }



# 自定义Django认证后端类
class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        username:用户名或手机号
        """
        # 根据用户名或手机号查询用户的信息
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
        except User.DoesNotExist:
            return None


        # 如果用户存在，在校验密码
        if user.check_password(password):
            # 密码正确
            return user