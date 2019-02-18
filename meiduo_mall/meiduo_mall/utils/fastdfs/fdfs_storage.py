# 自定义文件存储类
from django.core.files.storage import Storage,FileSystemStorage
from django.utils.deconstruct import deconstructible
from fdfs_client.client import Fdfs_client
from django.conf import settings


@deconstructible
class FDFSStorage(Storage):
    """FDFS文件存储类"""


    def __init__(self, client_conf=None, base_url=None):
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

        if base_url is None:
            base_url = settings.FDFS_NGINX_URL
        self.base_url = base_url


    def _save(self, name, content):
        """
        name:上传文件的名称:1.jpg
        content:包含上传文件内容FILE对象,可以通过content.read()获取上传文件的内容
        """
        # 将文件上传到FDFS系统
        # client = Fdfs_client("客户端配置文件路径")
        # client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        client = Fdfs_client(self.client_conf)

        res = client.upload_by_buffer(content.read())

        # 判断上传文件是否成功
        if res.get('Status') != 'Upload successed.':
            raise Exception("上传文件到FDFS失败")

        # 获取文件id
        file_id = res.get('Remote file_id')
        return file_id


    def exists(self, name):
        """
        Django在调用_save之前,会先调用exists方法,判断name和文件系统中原有文件是否同名
         name:上传文件的名称  1.jpg
        """
        return False


    def url(self, name):
        """
        返回可访问到文件存储系统中文件完整url地址
        name:表中image字段存储的内容
        """
        # return settings.FDFS_NGINX_URL + name
        return self.base_url + name