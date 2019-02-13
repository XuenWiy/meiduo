from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

# 自定以用户模型类，继承自AbstractUser
class User(AbstractUser):
     mobile = models.CharField(max_length=11, verbose_name="手机号")

     class Meta:
         db_table = 'tb_users'
         verbose_name = '用户'
         verbose_name_plural = verbose_name