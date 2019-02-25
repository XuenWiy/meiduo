from decimal import Decimal
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from goods.models import SKU
from orders.serializers import OrderSKUSerializer, OrderSerializer


# POST  /orders/
class OrderView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = OrderSerializer

    def post(self, request):
        """
        订单数据保存
         1.获取参数并进行校验(参数完整性,address是否存在,pay_method是否合法)
         2.保存订单的数据
         3.返回应答, 订单创建成功
        """
        # 1.获取参数并进行校验(参数完整性,address是否存在,pay_method是否合法)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        #  2.保存订单的数据
        serializer.save()

        #  3.返回应答, 订单创建成功
        return Response(serializer.data, status=status.HTTP_201_CREATED)



# GET  /orders/settlement/
class OrderSettlementView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        """
        获取登录用户结算商品的数据:
        1.从登录用户的redis购物车记录中获取用户购物车中被勾选的商品id和对应数量count
        2.根据商品id获取对应的商品数据并组织运费
        3.将数据序列化并返回
        """
        # 获取登录用户
        user = request.user

        # 1.从登录用户的redis购物车记录中获取用户购物车中被勾选的商品id和对应数量count
        # 获取redis链接
        redis_conn = get_redis_connection('cart')

        # 从redis set中获取用户购物车中被勾选的商品的id
        cart_selected_key = 'cart_selected_%s' % user.id

        sku_ids = redis_conn.smembers(cart_selected_key)

        # 从redis hash中获取用户购物车中添加的所有商品的id和对应数量count
        cart_key = 'cart_%s' % user.id
        cart_redis = redis_conn.hgetall(cart_key)

        # 组织数据
        cart_dict = {}
        for sku_id,count in cart_redis.items():
            cart_dict[int(sku_id)] = int(count)


        # 2.根据商品id获取对应的商品数据并组织运费
        skus = SKU.objects.filter(id__in=sku_ids)

        for sku in skus:
            # 给sku对象增加属性count,保存该商品所要结算的数量
            sku.count = cart_dict[sku.id]

        serializer = OrderSKUSerializer(skus, many=True)

        # 组织运费:10
        freight = Decimal(10.0)

        # 3.将数据序列化并返回
        res_data = {
            'freight':freight,
            'skus':serializer.data
        }

        return Response(res_data)