from rest_framework import serializers

from goods.models import SKU


class CartSerializer(serializers.Serializer):
    """购物车序列化器类"""
    sku_id = serializers.IntegerField(label='商品编号')
    count = serializers.IntegerField(label='商品数量')
    selected = serializers.BooleanField(label='勾选状态', default=True)

    def validate(self, attrs):
        # sku_id商品是否存在
        sku_id = attrs['sku_id']

        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        # 商品库存是否足够
        count = attrs['count']

        if count > sku.stock:
            raise serializers.ValidationError("商品库存不足")

        return attrs



class CartSKUSerializer(serializers.ModelSerializer):
    """购物车商品序列化器类"""
    count = serializers.IntegerField(label='数量')
    selected = serializers.BooleanField(label='勾选状态')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'count', 'selected')



class CartDelSerializer(serializers.Serializer):
    """购物车记录删除序列化器类"""
    sku_id = serializers.IntegerField(label='SKU商品ID')

    def validate_sku_id(self, value):
        # 商品是否存在
        try:
            sku = SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        return value



class CartSelectSerializer(serializers.Serializer):
    """购物车记录全选序列化器类"""
    selected = serializers.BooleanField(label='勾选状态')
