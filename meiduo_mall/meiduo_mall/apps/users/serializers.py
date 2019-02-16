import re

from django_redis import get_redis_connection
from rest_framework import serializers

from celery_tasks.email.tasks import send_verify_email
from users.models import User, Address


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

    # 用户名不能全部为数字
    def validate_username(self,value):
        if re.match('^\d+$',value):
            raise serializers.ValidationError('用户名不能全部为数字')
        return value

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



class UserDetailSerializer(serializers.ModelSerializer):

    """用户序列化器类"""
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')



class EmailSerializer(serializers.ModelSerializer):
    """邮箱设置序列化器类"""
    class Meta:
        model = User
        fields = ('id', 'email',)

        extra_kwargs = {
            'email':{
                'required':True
            }
        }


    # 设置登录用户的邮箱并且给邮箱发送验证邮件
    def update(self, instance, validated_data):
        # 设置登录用户的邮箱
        email = validated_data['email']
        instance.email = email
        instance.save()

        # TODO给邮箱发送验证邮件
        # 验证链接：http://www.meiduo.site:8080/success_verify_email.html?user_id=<用户id>
        # 如果直接将用户的id放在验证链接中,可能会发生恶意请求
        # 将用户的信息进行加密用 itsdangerous,然后把加密之后的内容放在验证链接中
        # http://www.meiduo.site:8080/success_verify_email.html?token=<加密用户的信息>
        # 生成邮箱链接地址
        verify_url = instance.generate_verify_email_url()

        # 发送邮件
        send_verify_email.delay(email, verify_url)

        return instance



class AddressSerializer(serializers.ModelSerializer):
    """地址序列化器类"""
    province_id = serializers.IntegerField(label='省id')
    city_id = serializers.IntegerField(label='市id')
    district_id = serializers.IntegerField(label='区县id')

    province = serializers.StringRelatedField(label='省', read_only=True)
    city = serializers.StringRelatedField(label='市', read_only=True)
    district = serializers.StringRelatedField(label='区县', read_only=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        # 手机号格式
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        # 创建并保存新增地址数据

        # 获取登录用户对象
        user = self.context['request'].user
        validated_data['user'] = user

        # 调用ModelSerializer中create方法
        addr = super().create(validated_data)

        return addr


class AddressTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', "title")