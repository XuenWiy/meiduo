from rest_framework import serializers
from goods.models import SKU
from drf_haystack.serializers import HaystackSerializer
from goods.search_indexes import SKUIndex


class SKUSerializer(serializers.ModelSerializer):
    """ SKU商品序列化器类"""
    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')



class SKUIndexSerializer(HaystackSerializer):
    """搜索结果的序列化器类"""
    object = SKUSerializer(label='商品')

    class Meta:
        # 指定索引类
        index_classes = [SKUIndex]
        fields = ('text', 'object')