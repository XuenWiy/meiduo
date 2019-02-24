
from rest_framework import serializers

from goods.models import SKU

class OrderSKUSerializer(serializers.ModelSerializer):
    """订单结算商品序列化器类"""
    count = serializers.IntegerField(label='结算数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'count')
