from django.conf.urls import url
from . import views
from django.contrib.auth import logout
from django.conf.urls import include
from social_django.urls import urlpatterns as social_django_urls

app_name = 'cri'

urlpatterns = [
        url(r'login/', views.login.as_view(), name='login'),
        url(r'logout/', logout, {'next_page': '/'}, name="logout"),
        url(r'log/', views.log.as_view(), name="log"),
        url(r'', include('social_django.urls')),
        ]
