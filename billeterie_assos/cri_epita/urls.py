from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import LoginView
from django.conf.urls import include
from social_django.urls import urlpatterns as social_django_urls
app_name = 'cri'

urlpatterns = [
        url(r'logout/', LogoutView.as_view(), {'next_page': '/'}, name="logout"), 
        url(r'log/', views.log.as_view(), name="log"),
        url(r'logged/', views.logged.as_view(), name="logged"), 
        ]
