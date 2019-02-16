from celery import Celery

# 设置Django运行所依赖环境变量
import os
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

# 创建Ｃｅｌｅｒｙ类的对象
celery_app = Celery('eityh')

# 加载配置
celery_app.config_from_object('celery_tasks.config')

# 让celery worker启动是自动发现有那些任务函数
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])