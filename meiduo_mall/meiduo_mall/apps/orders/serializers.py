from datetime import datetime

from decimal import Decimal

from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods


class OrderSKUSerializer(serializers.ModelSerializer):
    """订单结算商品序列化器类"""
    count = serializers.IntegerField(label='结算数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'count')



class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器类"""
    class Meta:
        model = OrderInfo
        fields = ('address', 'pay_method', 'order_id')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }


    def create(self, validated_data):
        """保存订单的数据"""
        # 获取address和pay_method
        address = validated_data['address']
        pay_method = validated_data['pay_method']

        # 获取登录用户
        user = self.context['request'].user

        # 订单id:年月日时分秒+用户id
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + '%010d' % user.id

        # 订单商品总数和实付款
        total_count = 0
        total_amount = Decimal(0)

        # 运费:10
        freight = Decimal(10.0)

        # 支付状态
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:  # 货到付款
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND'] # 待发货
        else:  #  在线支付
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']  # 待支付



        # 1.向订单基本信息表中添加一条记录
        order = OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            address=address,
            total_count=total_count,
            total_amount=total_amount,
            freight=freight,
            pay_method=pay_method,
            status=status
        )


        # 2.订单中包含几个商品,就需要向订单商品表中添加几条记录
        # 获取redis链接
        redis_conn = get_redis_connection('cart')

        # 从redis set中获取用户购物车中被勾选的商品的id
        cart_selected_key = 'cart_selected_%s' % user.id

        sku_ids = redis_conn.smembers(cart_selected_key)

        # 从redis hash中获取用户购物车中添加的所有商品的id和对应数量count
        cart_key = 'cart_%s' % user.id
        cart_redis = redis_conn.hgetall(cart_key)

        for sku_id in sku_ids:
            # 获取用户所要购买的该商品的数量count
            count = cart_redis[sku_id]
            count = int(count)

            # 根据sku_id获取商品对象
            sku = SKU.objects.get(id=sku_id)

            # 商品库存判断
            if count > sku.stock:
                raise serializers.ValidationError('商品库存不足')

            # 减少商品库存,增加销量
            sku.stock -= count
            sku.sales += count
            sku.save()

            # 向订单商品表添加一条记录
            OrderGoods.objects.create(
                order=order,
                sku=sku,
                count=count,
                price=sku.price
            )

            # 累加计算订单中商品的总数量和总金额
            total_count += count
            total_amount += sku.price*count

        # 实付款
        total_amount += freight

        # 更新订单商品的总数量和实付款
        order.total_count = total_count
        order.total_amount = total_amount
        order.save()

        # 3.删除redis中对应购物车记录
        pl = redis_conn.pipeline()
        pl.hdel(cart_key, *sku_ids)
        pl.srem(cart_selected_key, *sku_ids)
        pl.execute()

        return order

