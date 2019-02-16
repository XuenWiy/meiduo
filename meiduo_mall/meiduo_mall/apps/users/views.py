from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import GenericAPIView,CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.viewsets import ViewSet, GenericViewSet

from users import constants
from users.serializers import UserSerializer, UserDetailSerializer, EmailSerializer, AddressSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated



class AddressViewSet(CreateModelMixin, GenericViewSet):
    """用户中心地址管理"""

    permission_classes = [IsAuthenticated]

    serializer_class = AddressSerializer

    # 用户中心地址的添加
    # POST   /addresses/
    def create(self, request):
        """
        登录用户地址的新增:
        1.获取参数并进行校验(参数完整性,手机号格式,邮箱格式)
        2.创建并保存新增地址数据
        3.将新增地址数据序列化并返回
        """
        # 判断用户的地址数量是否超过数量上限
        count = request.user.addresses.filter(is_deleted=False).count()

        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message':"地址数量超过上限"}, status=status.HTTP_400_BAD_REQUEST)

        # # 1.获取参数并进行校验(参数完整性,手机号格式,邮箱格式)
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        #
        # # 2.创建并保存新增地址数据
        # serializer.save()
        #
        # # 3.将新增地址数据序列化并返回
        # return Response(serializer.data, status=status.HTTP_201_CREATED)


        # 调用CreateModelMixin中create方法
        return super().create(request)





# 邮箱验证
# PUT  /emails/verification/?token=<加密用户的信息>
class EmailVerifyView(APIView):
    def put(self, request):
        """
        用户邮箱验证
         1.获取token并进行验证(token必传, token是否有效)
         2.设置对应用户的邮箱验证标记email_active为True
         3.返回应答,验证成功
        """
        # 1.获取token并进行验证(token必传, token是否有效)
        token = request.query_params.get('token')

        if token is None:
            return Response({'message':'缺少token参数'}, status=status.HTTP_400_BAD_REQUEST)

        # 对token进行解密
        user = User.check_email_verify_token(token)

        if user is None:
            return Response({"message": '无效的ddtoken'}, status=status.HTTP_400_BAD_REQUEST)

        #  2.设置对应用户的邮箱验证标记email_active为True
        user.email_active = True
        user.save()

        #  3.返回应答,验证成功
        return Response({'message':'OK'})



# PUT  /email/
class EmailView(UpdateAPIView):
    # drf　中权限认证
    permission_classes = [IsAuthenticated]

    serializer_class = EmailSerializer

    def get_object(self):
        """返回登录用户对象"""
        return self.request.user

    # def put(self, request):
    #     """
    #     登录用户的邮箱设置
    #     １．获取参数并进行校验(email必传,email格式)
    #     ２．设置登录用户的邮箱并且给邮箱发送验证邮件
    #     ３．返回应答，邮箱设置成功
    #     """
    #     # 获取登录用户
    #     user = self.get_object()
    #
    #     #１．获取参数并进行校验(email必传,email格式)
    #     serializer = self.get_serializer(user, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     # ２．设置登录用户的邮箱
    #     serializer.save()
    #
    #     # ３．返回应答，邮箱设置成功
    #     return Response(serializer.data)





# 用户中心个人资料显示
# GET  /user/
class UserDetailView(RetrieveAPIView):
    # drf　中权限认证
    permission_classes = [IsAuthenticated]

    serializer_class = UserDetailSerializer

    def get_object(self):
        """返回登录用户对象"""
        # self.request:request请求对象
        return self.request.user


    # def get(self, request):
    #     return self.retrieve(request)

    # def get(self, request):
    #     """
    #     获取登录用户基本信息
    #     1.获取登录用户
    #     2.将登录用户对象序列化并返回
    #     """
    #     # 1.获取登录用户
    #     user = self.get_object()
    #
    #     # 2.将登录用户对象序列化并返回
    #     serializer = self.get_serializer(user)
    #
    #     return Response(serializer.data)




# 登录功能
# POST /authorizations/
# class UserAuthorizeView(APIView):
#     def post(self,request):
#         """
#         用户登录
#         １．获取参数username和password并进行校验(参数完整性,用户名和密码是否正确)
#         ２．生成jwt token保存登录用户身份信息
#         ３．返回响应，登录成功
#         """
#         # １．获取参数username和password并进行校验(参数完整性, 用户名和密码是否正确)
#         # ２．生成jwt token保存登录用户身份信息
#         # ３．返回响应，登录成功
#         pass



# 用户注册信息保存
# POST /users/
class UserView(CreateAPIView):
    # 指定视图所使用的序列化器类
    serializer_class = UserSerializer

    # def post(self,request):
    #     """
    #     注册用户信息的保存
    #     １．获取参数并进行校验(参数完整性,是否同意协议,手机号格式,手机号是该存在,两次密码是否一致,短信验证码是否正确)
    #     ２．创建新用户并保存到数据库
    #     ３．注册成功，将新用户序列化并返回
    #     """
    #     # １．获取参数并进行校验(参数完整性, 是否同意协议, 手机号格式, 手机号是该存在, 两次密码是否一致, 短信验证码是否正确)
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #
    #     # ２．创建新用户并保存到数据库
    #     serializer.save()
    #
    #
    #     # ３．注册成功，将新用户序列化并返回
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)



# 查询手机号是否已经注册
# GET /mobiles/(?P<mobile>1[3-9]\d{9})/count/
class MobileCountView(APIView):
    def get(self, request, mobile):
        """
        获取用户名数量：
         １．根据手机号查询数据库，获取查询结果数量
         ２．返回手机号数量
        """
        # １．根据手机号查询数据库，获取查询结果数量
        count = User.objects.filter(mobile=mobile).count()

        # ２．返回手机号数量
        res_data = {
            'mobile':mobile,
            'count':count
        }
        return Response(res_data)



# 查询用户名是否存在
# GET /usernames/(?P<username>\w{5,20})/count/
class UsernameCountView(APIView):
    def get(self, request, username):
        """
        获取用户名数量：
         １．根据用户名查询数据库，获取查询结果数量
         ２．返回用户名数量
        """
        # １．根据用户名查询数据库，获取查询结果数量
        count = User.objects.filter(username=username).count()

        # ２．返回用户名数量
        res_data = {
            'username':username,
            'count':count
        }
        return Response(res_data)
