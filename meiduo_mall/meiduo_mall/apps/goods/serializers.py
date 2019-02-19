

from rest_framework import serializers

from goods.models import SKU

class SKUSerializer(serializers.ModelSerializer):
    """ SKU商品序列化器类"""
    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')
