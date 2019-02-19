from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.


# GET  /categories/(?P<category_id>\d+)/skus/
from goods.models import SKU
from goods.serializers import SKUSerializer


class SKUListView(ListAPIView):

    serializer_class = SKUSerializer

    def get_queryset(self):
        """返回第三级分类ID分类SKU商品的数据"""
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id)

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