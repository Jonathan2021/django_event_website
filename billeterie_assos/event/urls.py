from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'event'


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('event/', login_required(views.MyAssosView.as_view()), name='my_assos'),
]
