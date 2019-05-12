from django.urls import path
from django.conf.urls import url
from django.contrib import admin
from social_django.urls import urlpatterns as social_django_urls
from django.contrib.auth.views import logout
from . import views

app_name = 'event'


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^', include(social_django_urls, namespace='social')),
    url(r'logout/', logout, {'next_page': '/'}, name="logout"),
    url(r'^', include('example.urls')),
]
