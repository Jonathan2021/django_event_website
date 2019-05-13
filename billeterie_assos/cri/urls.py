from django.conf.urls import url
from .views import logged
from . import views

app_name = 'cri'

urlpatterns = [
        url(r'^$', views.logged, name='home'),
        url(r'^login/$', views.login, name='logged'),
]
