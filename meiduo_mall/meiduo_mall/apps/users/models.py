from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
from itsdangerous import BadData
from django.conf import settings


# Create your models here.

# 自定以用户模型类，继承自AbstractUser
from meiduo_mall.utils.models import BaseModel
from users import constants


class User(AbstractUser):
     mobile = models.CharField(max_length=11, verbose_name="手机号")
     email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
     default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
                                         on_delete=models.SET_NULL, verbose_name='默认地址')

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

         verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token

         return verify_url


     # 对验证邮箱中token进行解密
     @staticmethod
     def check_email_verify_token(token):
         """
         对加密用户信息进行解密
         token:加密用户的信息
         """
         serializer = TJWSSerializer(secret_key=settings.SECRET_KEY)

         try:
             data = serializer.loads(token)
         except BadData:
             # 解密失败
             return None
         else:
             # 解密成功
             user_id = data['user_id']
             email = data['email']

             try:
                 user = User.objects.get(id=user_id, email=email)
             except User.DoesNotExist:
                 return None
             else:
                 return user





class Address(BaseModel):
    """
    用户地址
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', related_name='province_address', on_delete=models.PROTECT, verbose_name='省')
    city = models.ForeignKey('areas.Area', related_name='city_address', on_delete=models.PROTECT, verbose_name='市')
    district = models.ForeignKey('areas.Area', related_name='district_address', on_delete=models.PROTECT, verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']