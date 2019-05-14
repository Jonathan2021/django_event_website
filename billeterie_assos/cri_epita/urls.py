from django.conf.urls import url
from . import views
from django.contrib.auth import logout

app_name = 'cri'

urlpatterns = [
        url(r'login/', views.login.as_view(), name='login'),
        url(r'logout/', logout, {'next_page': '/'}, name="logout"),
        url(r'log/', views.log.as_view(), name="log"),
]
