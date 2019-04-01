from django.conf.urls import include, path

from . import views


app_name='event'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]
