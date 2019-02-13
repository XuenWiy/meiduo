# 封装ｃｅｌｅｒｙ任务函数
from rest_framework import status

from celery_tasks.sms.yuntongxun.sms import CCP
from celery_tasks.main import celery_app

# 短信发送模板ID
SEND_SMS_TEMP_ID = 1

# 获取日志器
import logging
logger = logging.getLogger('django')


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code, expires):
    # 任务函数代码

    try:
        res = CCP().send_template_sms(mobile, [sms_code, expires], SEND_SMS_TEMP_ID)
    except Exception as e:
        logger.error('短信验证码发送异常：[mobile:%s sms_code:%s]' % (mobile,sms_code))
    else:
        if res != 0:
            # 短信发送失败
            logger.error('短信验证码发送失败：[mobile:%s sms_code:%s]' % (mobile, sms_code))
        else:
            logger.info('短信验证码发送成功：[mobile:%s sms_code:%s]' % (mobile, sms_code))

