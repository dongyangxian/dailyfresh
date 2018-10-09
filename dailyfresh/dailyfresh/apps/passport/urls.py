from django.conf.urls import url
from dailyfresh.apps.passport import views
urlpatterns = [
    # 每个路由信息都需要使用url函数来构造
    # url(路径, 视图)
    url(r'^imagecodes/(?P<image_id>\S+)/$', views.SendImageIdView.as_view()),
]