from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView
from . import views
from django.contrib.auth import logout
from django.conf.urls import include
from social_django.urls import urlpatterns as social_django_urls
app_name = 'cri'

urlpatterns = [
        url(r'login/', views.login.as_view(), name='login'),
        url(r'logout/', logout, {'next_page': '/'}, name="logout"), 
        path('log/', TemplateView.as_view(template_name="log.html")),
        url(r'log/', views.log.as_view(), name="log"),
        url(r'^', include((social_django_urls,'cri_epita'), namespace='social'))
        ]
