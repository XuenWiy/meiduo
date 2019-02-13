from celery import Celery

# 创建Ｃｅｌｅｒｙ类的对象
celery_app = Celery('eityh')

# 加载配置
celery_app.config_from_object('celery_tasks.config')

# 让celery worker启动是自动发现有那些任务函数
celery_app.autodiscover_tasks(['celery_tasks.sms'])