from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
from django.conf import settings

# Create your models here.

# 自定以用户模型类，继承自AbstractUser
from users import constants


class User(AbstractUser):
     mobile = models.CharField(max_length=11, verbose_name="手机号")
     email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

     class Meta:
         db_table = 'tb_users'
         verbose_name = '用户'
         verbose_name_plural = verbose_name

     def generate_verify_email_url(self):
         """生成用户的邮箱验证链接地址"""
         data = {
             "user_id":self.id,
             "email":self.email

         }

         serializer = TJWSSerializer(secret_key=settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)

         # 对用户的信息进行加密
         token = serializer.dumps(data) # bytes
         token = token.decode() # bythes->str

         verify_url = 'http://www.meiduo.site:8000/success_verify_email.html?token=' + token

         return verify_url