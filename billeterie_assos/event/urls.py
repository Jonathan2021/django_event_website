from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'event'


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('my_assos/', login_required(views.MyAssosView.as_view()), name='my_assos'),
    path('assos/<int:pk>', views.AssosDetailView.as_view(), name='asso_detail'),
    path('assos/', views.AssosView.as_view(), name='assos'),
]
