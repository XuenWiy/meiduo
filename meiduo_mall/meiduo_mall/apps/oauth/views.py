from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from oauth.exceptions import QQAPIError
from oauth.models import OAuthQQUser
from oauth.serializers import QQAuthUserSerializer
from oauth.utils import OAuthQQ
from rest_framework.views import APIView

# 获取QQ登录用户 openid并处理
# GET   /oauth/qq/user/?code=<code>
class QQAuthUserView(GenericAPIView):
    # 指定当前视图所使用的序列化器类
    serializer_class = QQAuthUserSerializer
    def post(self, request):
        """
        保存QQ登录绑定数据
        １．获取参数并进行校验(参数完整性,手机号格式,短信验证码是否正确,access_token是否有效)
        ２．保存QQ绑定的数据
        ３．返回应答，绑定成功
        """
        # １．获取参数并进行校验(参数完整性,手机号格式,短信验证码是否正确,access_token是否有效)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        # ２．保存QQ绑定的数据
        serializer.save()

        # ３．返回应答，绑定成功
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    # 返回QQ登录后的界面(回调地址或绑定用户地址)
    def get(self, request):
        """
        # 获取QQ登录用户openid并处理
        １．获取code并校验(code)
        ２．获取QQ登录用户的openid
            2.1通过code请求QQ服务器获取access_token
            2.2通过access_token请求QQ服务器获取openid
        ３．根据openid判断是否绑定过本网站的用户
            3.1 如果已绑定，直接生成jwt token并返回
            3.2 如果未绑定，将openid加密并返回
        """
        # １．获取code并校验(code)
        code = request.query_params.get('code')

        # 判断是否有code
        if code is None:
            return Response({'message':'未携带code'}, status=status.HTTP_400_BAD_REQUEST)



        # ２．获取QQ登录用户的openid
        oauth = OAuthQQ()

        try:
            # 2.1 通过code请求QQ服务器获取access_token
            access_token = oauth.get_access_token(code)

            # 2.2 通过access_token请求QQ服务器获取openid
            openid = oauth.get_openid(access_token)
        except QQAPIError:
            return Response({'message':'QQ登录异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


        # ３．根据openid判断是否绑定过本网站的用户
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 3.2 如果未绑定，将openid加密并返回
            secret_openid = OAuthQQ.generate_save_user_token(openid)
            return Response({'access_token':secret_openid})

        else:
            # 3.1 如果已绑定，直接生成jwt token并返回
            user = qq_user.user
            # 由服务器生成一个jwt token,保存用户身份信息
            from rest_framework_jwt.settings import api_settings

            # 生成payload的方法
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            # 生成jwt token的方法
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            # 生成payload
            payload = jwt_payload_handler(user)
            # 生成jwt token
            token = jwt_encode_handler(payload)

            # 返回应答
            res_data = {
                'user_id':user.id,
                'username':user.username,
                'token':token
            }

            return Response(res_data)


# 访问QQ登录页面
# GET  /oauth/qq/authorization/?next=<登录之后访问页面地址>
class QQAuthURLView(APIView):
    def get(self, request):
        """
        获取ＱＱ登录网址
        １．获取ｎｅｘｔ
        ２．组织ＱＱ登录网址和参数
        ３．返回ＱＱ登录网址
        """
        # １．获取ｎｅｘｔ
        next = request.query_params.get('next','/')


        # ２．组织ＱＱ登录网址和参数
        oauth = OAuthQQ(state=next)
        login_url = oauth.get_login_url()


        # ３．返回ＱＱ登录网址
        return Response({'login_url':login_url})
