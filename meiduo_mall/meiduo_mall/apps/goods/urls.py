from django.conf.urls import url
from goods import views

urlpatterns = [
    url(r'^categories/(?P<category_id>\d+)/skus/', views.SKUListView.as_view()),


]

# 路由Router
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('skus/search', views.SKUSearchViewSet, base_name='skus_search')
urlpatterns += router.urls