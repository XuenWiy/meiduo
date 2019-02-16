from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from areas.models import Area
from areas.serializers import AreaSerializer
# Create your views here.



# GET  /areas/
class AreasView(ListAPIView):
    serializer_class = AreaSerializer
    queryset = Area.objects.filter(parent=None)

    # def get(self, request):
    #     """
    #     获取所有省级地址的信息
    #     1.查询所有省级地区的信息
    #     2.将省级地区的数据序列化并返回
    #     """
    #     #1 .查询所有省级地区的信息
    #     areas = self.get_queryset()
    #
    #     # 2.将省级地区的数据序列化并返回
    #     serializers = self.get_serializer(areas, many=True)
    #     return Response(serializers.data)