import re

from django_redis import get_redis_connection
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器类"""

    password2 = serializers.CharField(label='重复密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label="JWT token", read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'mobile', 'password2', 'sms_code', 'allow', 'token')

        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    # 是否同意协议, 手机号格式, 手机号是该存在, 两次密码是否一致, 短信验证码是否正确
    def validate_allow(self, value):
        # 是否同意协议
        if value != 'true':
            raise serializers.ValidationError('请同意协议')
        return value

    def validate_mobile(self,value):
        # 手机号格式, 手机号是该存在
        if not re.match(r'1[3-9]\d{9}$', value):
            raise serializers.ValidationError('请输入正确手机号')
        if User.objects.filter(mobile=value).count() != 0:
            raise serializers.ValidationError('手机号已注册')
        return value

    def validate(self, attrs):
        # 两次密码是否一致, 短信验证码是否正确
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise  serializers.ValidationError('两次密码不一致')

        # 短信验证码是否正确
        mobile = attrs.get('mobile')

        # 从redis中获取真实的验证码内容
        redis_conn = get_redis_connection("verify_codes")
        real_sms_code = redis_conn.get('sms_%s' % mobile) #  bytes

        # 判断短信验证码是否过期
        if real_sms_code is None:
            raise serializers.ValidationError('短信验证码以过期')

        user_sms_code = attrs.get('sms_code')



        if real_sms_code.decode() != user_sms_code:
            raise serializers.ValidationError('验证码填写错误')

        return attrs


    def create(self, validated_data):
        """
        创建新用户并保存到数据库
        validated_data:校验之后的数据
        """
        # 清除不需要保存的数据
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # 创建新用户并保存到数据库
        user = User.objects.create_user(**validated_data)

        # 由服务器生成一个jwt token,保存用户身份信息
        from rest_framework_jwt.settings import api_settings

        # 生成payload的方法
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        # 生成jwt token的方法
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        # 生成payload
        payload = jwt_payload_handler(user)
        #生成jwt token
        token = jwt_encode_handler(payload)

        # 给user对象增加属性token,保存jwt token的数据
        user.token = token

        return user




