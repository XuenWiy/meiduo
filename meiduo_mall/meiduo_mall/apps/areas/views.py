from django.http import Http404
from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from areas.models import Area
from areas.serializers import AreaSerializer, SubAreaSerializer
from rest_framework.mixins import RetrieveModelMixin

# Create your views here.


# 用视图集实现省市县地区查询
class AreasViewSet(ReadOnlyModelViewSet):
    """地区视图集"""
    def get_serializer_class(self):
        """获取视图所使用的序列化器类"""
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubAreaSerializer

    def get_queryset(self):
        """获取视图所使用的查询集"""
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()




# 获取市或县地区信息
# GET  /areas/(?P<pk>\d+)/
class SubAreasView(RetrieveAPIView):

    serializer_class = SubAreaSerializer
    queryset = Area.objects.all()

    # def get(self, request, pk):
    #     """
    #     获取指定地区的信息
    #     1.根据pk查询指定地区的信息
    #     """
    #     # 1.根据pk查询指定地区的信息
    #     # try:
    #     #     area = Area.objects.get(pk=pk)
    #     # except Area.DoesNotExist:
    #     #     raise Http404
    #
    #     area = self.get_object()
    #
    #
    #     # 2.将地区数据序列化并返回(地区下级地区需要进行嵌套序列化)
    #
    #     serializers = self.get_serializer(area)
    #     return Response(serializers.data)



# 获取所有省级地区信息
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