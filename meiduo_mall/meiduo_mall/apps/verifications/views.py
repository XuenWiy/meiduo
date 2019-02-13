from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from verifications import constants
from meiduo_mall.libs.yuntongxun.sms import CCP
import random

# Create your views here.

# 获取日志器
import logging
logger = logging.getLogger('django')

# 获取短信验证码
# GET /sms_codes/(?P<mobile>1[3-9]\d{9})/
class SMSCodeView(APIView):
    def get(self, request, mobile):
        """
        获取短信验证码：
         １．随机生成６位数字作为短信验证码
         2．在redis中存储短信验证码内容，以'sms_<mobile>'为key,以验证码内容为ｖａｌｕｅ
         3．使用云通讯给ｍｏｂｉｌｅ发送短信
        ４．返回应答，短信发送成功
        """
        # 获取ｒｅｄｉｓ存储链接
        redis_conn = get_redis_connection('verify_codes')

        # 判断ｍｏｂｉｌｅ是否在６０秒内发送过短信
        if redis_conn.get('send_flag_%s' % mobile):
            return Response({'message':'短信发送过于频繁'}, status=status.HTTP_403_FORBIDDEN)


        # １．随机生成６位数字作为短信验证码
        sms_code = '%6d' % random.randint(0,999999)
        print(sms_code)


        #  2．在redis中存储短信验证码内容，以'sms_<mobile>'为key,以验证码内容为ｖａｌｕｅ
        # 把短信验证码存储到ｒｅｄｉｓ中的方法
        # redis_conn.set('<key>', '<value>', '<expires>')
        # redis_conn.setex('<key>', '<expires>', '<value>')

        # redis管道使用，多个ｒｅｄｉｓ命令一次提交
        # 创建redis管道对象
        pl = redis_conn.pipeline()

        # 向redis管道中添加命令
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 设置同一手机号最短发送短信标记
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, mobile)

        # 一次性执行管道中的所有命令
        pl.execute()

        #  3．使用云通讯给ｍｏｂｉｌｅ发送短信
        expires = constants.SMS_CODE_REDIS_EXPIRES // 60

        # 发出发送短信任务消息
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile, sms_code, expires)

        # ４．返回应答，短信发送成功
        return Response({'message': 'OK'})
