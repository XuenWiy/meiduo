import base64
import pickle

from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from cart.serializers import CartSerializer, CartSKUSerializer, CartDelSerializer, CartSelectSerializer
from cart import constants
from goods.models import SKU



# PUT  /cart/selection
class CartSelectAllView(APIView):
    def perform_authentication(self, request):
        """让当前视图跳转DRF框架默认认证过程"""
        pass

    def put(self, request):
        """
        购物车记录全选和取消全选
        1.获取参数selected并进行校验(selected必传)
        2.设置用户购物车记录勾选状态
            2.1如果用户已登录,设置redis中用户购物车记录勾选状态
            2.2如果用户未登录,设置cookie中用户购物车记录勾选状态
        3.返回应答,设置成功
        """
        # 1.获取参数selected并进行校验(selected必传)
        serializer = CartSelectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取校验之后的selected
        selected = serializer.validated_data['selected']

        try:
            user = request.user
        except Exception:
            user = None

        # 2.设置用户购物车记录勾选状态
        if user and user.is_authenticated:

            # 2.1如果用户已登录,设置redis中用户购物车记录勾选状态
            redis_conn = get_redis_connection('cart')

            # 从redis hash中获取用户购物车中所有商品的id
            cart_key = 'cart_%s' % user.id
            sku_ids = redis_conn.hkeys(cart_key)

            cart_selected_key = 'cart_selected_%s' % user.id

            if selected:
                # 全选:将用户购物车所有商品的id添加到redis set中
                redis_conn.sadd(cart_selected_key, *sku_ids)

            else:
                # 全不选:将用户购物车所有商品的id从redis set中移除
                redis_conn.srem(cart_selected_key, *sku_ids)

            return Response({'message':'OK'})


        else:
            # 2.2如果用户未登录,设置cookie中用户购物车记录勾选状态
            # 获取cookie的购物车记录
            cookie_cart = request.COOKIES.get('cart')

            if cookie_cart:
                # 解析cookie中的购物车数据
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))

            else:
                cart_dict = {}

            # 设置cookie购物车记录勾选状态
            for sku_id, count_selected in cart_dict.items():
                cart_dict[sku_id]['selected'] = selected


            # 3.返回应答,设置成功
            response = Response({'message':'OK'})
            # 设置cookie中的购物车数据
            cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('cart', cart_data, max_age=constants.CART_COOKIE_EXPIRES)

            return response




# 购物车
# /cart/
class CartView(APIView):

    def perform_authentication(self, request):
        """重写父类perform_authentication,让当前视图跳过DRF框架认证过程"""
        pass


    # DELETE  /cart/
    def delete(self, request):
        """
        购物车记录删除
        1. 获取商品sku_id并进行校验(sku_id必传,sku_id对应商品是否存在)
        2.删除用户的购物车记录
            2.1如果用户已登录,删除redis中对应的购物车记录
            2.2如果用户未登录,删除cookie中对应的购物车记录
        3.返回应答,购物车记录删除成功
        """
        # 1. 获取商品sku_id并进行校验(sku_id必传,sku_id对应商品是否存在)
        serializer = CartDelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取校验之后的数据
        sku_id = serializer.validated_data['sku_id']

        try:
            user = request.user
        except Exception:
            user = None

        # 2.删除用户的购物车记录
        if user and user.is_authenticated:

            # 2.1如果用户已登录,删除redis中对应的购物车记录
            # 获取redis链接
            redis_conn = get_redis_connection('cart')

            # 从redis hash中删除对应商品的id和数量count
            cart_key = 'cart_%s' % user.id
            redis_conn.hdel(cart_key, sku_id)

            # 从redis set中删除对应商品的id
            cart_selected_key = 'cart_selected_%s' % user.id
            redis_conn.srem(cart_selected_key, sku_id)

            return Response(status=status.HTTP_204_NO_CONTENT)



        else:
            # 2.2如果用户未登录,删除cookie中对应的购物车记录
            response = Response(status=status.HTTP_204_NO_CONTENT)

            # 获取cookie中的购物车记录
            cookie_cart = request.COOKIES.get('cart')

            if cookie_cart is None:
                # 购物车无数据
                return response

            # 解析cookie中购物车数据
            cart_dict = pickle.loads(base64.b64decode(cookie_cart))

            if sku_id in cart_dict:
                del cart_dict[sku_id]
                # 重新设置cookie购物车数据
                cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode()
                response.set_cookie('cart', cart_data, max_age=constants.CART_COOKIE_EXPIRES)


            # 3.返回应答,购物车记录删除成功

            return response




    def put(self, request):
        """
        购物车记录修改:
        1.获取参数并进行校验(参数完整性,sku_id商品是否存在,商品的库存)
        2.修改用户的购物车记录
            2.1如果用户以登录,修改redis中对应的购物车记录:
            2.2如果用户未登录,修改cookie中对应的购物车记录
        3.返回应答,购物车记录修改成功
        """
        # 1.获取参数并进行校验(参数完整性,sku_id商品是否存在,商品的库存)
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取校验之后的数据
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        selected = serializer.validated_data['selected']

        # 获取user
        try:
            # 调用request.user会触发DRF框架认证过程
            user = request.user
        except Exception:
            user = None


        # 2.修改用户的购物车记录
        if user and user.is_authenticated:
            # 2.1如果用户以登录,修改redis中对应的购物车记录
            # 获取redis链接
            redis_conn = get_redis_connection('cart')

            # 修改redis hash中商品id对应数量count
            cart_key = 'cart_%s' % user.id
            redis_conn.hset(cart_key, sku_id, count)

            # 修改redis set中勾选的商品id
            cart_selected_key = 'cart_selected_%s' % user.id

            if selected:
                # 勾选
                redis_conn.sadd(cart_selected_key, sku_id)
            else:
                # 取消勾选
                redis_conn.srem(cart_selected_key, sku_id)

            return Response(serializer.validated_data)

        else:
        # 2.2如果用户未登录,修改cookie中对应的购物车记录
            response = Response(serializer.validated_data)
            # 获取cookie中的购物车数据
            cookie_cart = request.COOKIES.get('cart')
            if cookie_cart is None:
                # 购物车中无数据
                return response
            cart_dict = pickle.loads((base64.b64decode(cookie_cart)))
            if not cart_dict:
                # 字典为空,购物车无数据
                return response

            # 修改购物车数据
            cart_dict[sku_id] = {
                'count':count,
                'selected':selected
            }

            #  3.返回应答,购物车记录修改成功
            # 设置cookie中购物车数据
            cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('cart', cart_data, max_age=constants.CART_COOKIE_EXPIRES)

            return response


    # GET /
    def get(self, request):
        """
        购物车记录获取
        1.获取用户的购物车记录
            1.1如果用户以登录,从redis中获取用户的购物车记录
            1.2rug用户未登录,从cookie中获取用户的购物车记录
        2.根据用户购物车中商品id获取对应商品的数据
        3.将购物车商品的数据序列化并返回
        """
        try:
            user = request.user
        except Exception:
            user = None

        # 1.获取用户的购物车记录
        if user and user.is_authenticated:
            #1.1如果用户以登录,从redis中获取用户的购物车记录
            #获取redis链接
            redis_conn = get_redis_connection('cart')

            # 从redis 哈市中获取用户购物车中添加的商品id和对应的数量count
            cart_key = 'cart_%s' % user.id

            # {
            #     b'<sku_id>':b'<count>',
            #     ...
            # }
            cart_redis = redis_conn.hgetall(cart_key)

            # 从redis set中获取用户购物车中勾选的商品id
            cart_selected_key = 'cart_selected_%s' % user.id

            cart_selected_redis = redis_conn.smembers(cart_selected_key)

            # {
            #     '<sku_id>':{
            #         'count':'<count>',
            #         'selected':'<selected>'
            #     },
            #     ...
            # }
            cart_dict = {}
            for sku_id,count in cart_redis.items():
                cart_dict[int(sku_id)] = {
                    'count':int(count),
                    'selected':sku_id in cart_selected_redis
                }


        else:
            #1.2rug用户未登录,从cookie中获取用户的购物车记录
            # 获取cookie中的购物车数据
            cookie_cart = request.COOKIES.get('cart')

            if cookie_cart:
                # 解析cookie中购物车数据
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))
            else:
                cart_dict = {}


        # 2.根据用户购物车中商品id获取对应商品的数据
        sku_ids = cart_dict.keys()

        skus = SKU.objects.filter(id__in=sku_ids)

        for sku in skus:
            # 给sku对象增加属
            # 性count和selected,分别保存该商品在购物车中添加数量和勾选状态
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']

        # 3.将购物车商品的数据序列化并返回
        serializer = CartSKUSerializer(skus, many=True)

        return Response(serializer.data)


    # POST
    def post(self, request):
        """
        购物车记录添加
        1.获取参数并进行校验(参数完整性, sku_id商品是否存在,商品库存是否足够)
        2.保存用户的购物车记录
            2.1如果用户已登录,在redis中保存用户的购物车记录
            2.2如果用户未登录,在cookie中保存用户的购物车记录
        3.返回应答,购物车记录添加成功
        """
        # 1.获取参数并进行校验(参数完整性, sku_id商品是否存在,商品库存是否足够)
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 获取校验之后的数据
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        selected = serializer.validated_data['selected']

        # 获取user
        # 调用request.user会触发DRF框架认证过程
        try:
            user = request.user
        except Exception:
            user = None

        # 2.保存用户的购物车记录
        if user and user.is_authenticated:
            # 2.1如果用户已登录,在redis中保存用户的购物车记录

            # 获取redis链接
            redis_conn = get_redis_connection('cart')

            # hash:在redis hash中存储用户购物车添加的商品id和数量count
            cart_key = 'cart_%s' % user.id

            # 如果购物车已经添加过该商品,数量需要进行累加,如果未添加,直接添加一个新元素
            redis_conn.hincrby(cart_key, sku_id, count)

            # set:在redis set中存储用户购物车勾选商品的id
            cart_selected_key = 'cart_selected_%s' % user.id

            if selected:
                redis_conn.sadd(cart_selected_key, sku_id)

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


        else:
            # 2.2如果用户未登录,在cookie中保存用户的购物车记录
            # 获取cookie的购物车数据
            cookie_cart = request.COOKIES.get('cart')

            if cookie_cart:
                # 解析cookie中购物车数据
                # {
                #     '<sku_id>':{
                #         'count':'<count>',
                #         'selected':'<selected>'
                #     },
                #     ...
                # }
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))

            else:
                cart_dict = {}


            # 如果购物车已经添加过该商品,数量需要进行累加,如果未添加,直接添加一个新元素
            if sku_id in cart_dict:
                count += cart_dict[sku_id]['count']

            cart_dict[sku_id] = {
                'count':count,
                'selected':selected
            }


            # 3.返回应答,购物车记录添加成功
            response = Response(serializer.validated_data, status=status.HTTP_201_CREATED)

            # 设置cookie中购物车数据
            cart_data = base64.b64encode(pickle.dumps((cart_dict))).decode()
            response.set_cookie('cart', cart_data, max_age=constants.CART_COOKIE_EXPIRES)

            return response
