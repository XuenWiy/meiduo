from django.conf.urls import url
from users import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'^users/$', views.UserView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^user/$', views.UserDetailView.as_view()),
    url(r'^email/$', views.EmailView.as_view()),
    url(r'^email/verification/$', views.EmailVerifyView.as_view()),
    url(r'^browse_histories/$', views.BrowseHistoryView.as_view()),

]


# 路由Router
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('addresses', views.AddressViewSet, base_name='addresses')
urlpatterns += router.urls