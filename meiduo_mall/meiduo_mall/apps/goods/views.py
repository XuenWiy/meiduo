from django.shortcuts import render
from rest_framework.filters import OrderingFilter
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from goods.models import SKU
from goods.serializers import SKUSerializer, SKUIndexSerializer
from drf_haystack.viewsets import HaystackViewSet
# Create your views here.

# GET  /skus/search/?text=<搜索关键字>
class SKUSearchViewSet(HaystackViewSet):
    # 指定索引类对应模型类
    index_models = [SKU]

    # 指定搜索结果序列化是所使用的序列化器类
    serializer_class = SKUIndexSerializer


# GET  /categories/(?P<category_id>\d+)/skus/
class SKUListView(ListAPIView):

    serializer_class = SKUSerializer

    def get_queryset(self):
        """返回第三级分类ID分类SKU商品的数据"""
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id)


    # 排序
    filter_backends = [OrderingFilter]
    # 指定排序字段
    ordering_fields = ('create_time', 'price', 'sales')


    # def get(self, request, category_id):
    #     """
    #     根据第三级分类ID获取分类SKU商品的数据
    #     1.根据'category_id'获取分类SKU商品的数据
    #     2.将商品的数据序列化并返回
    #     """
    #     # 1.根据'category_id'获取分类SKU商品的数据
    #     # skus = SKU.objects.filter(category_id=category_id)
    #     skus = self.get_queryset()
    #
    #     # 2.将商品的数据序列化并返回
    #     serializer = self.get_serializer(skus, many=True)
    #
    #     return Response(serializer.data)