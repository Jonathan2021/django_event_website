from django.urls import path
from django.contrib.auth.decorators import login_required, permission_required
from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin
from social_django.urls import urlpatterns as social_django_urls
from ecommerce_app import views as com_views
from . import views

app_name = 'event'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('assos/mine/', login_required(views.MyAssosView.as_view()), name='my_assos'),
    url(r'^admin/', admin.site.urls),
    url(r'', include('cri_epita.urls', namespace="cri")),
    path('assos/<int:pk>', views.AssosDetailView.as_view(), name='asso_detail'),
    path('assos/', views.AssosView.as_view(), name='assos'),
    path('event/', views.EventListView.as_view(), name='events'),
    path('event/<int:pk>', views.EventDetailView.as_view(), name='event_detail'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('assos/delete/<int:pk>', permission_required('event.delete_association', login_url='login')(views.AssosDelete.as_view()), name='assos_delete'),
    path('assos/<int:asso_pk>/delete/member/<int:pk>', permission_required('event.delete_member', login_url='login')(views.MemberDelete.as_view()), name='delete_member'),
    path('assos/manager/add/<int:pk>', permission_required('event.add_manager', login_url='login')(views.ManagerCreate.as_view()), name='add_manager'),
    path('assos/<int:asso_pk>/delete/manager/<int:pk>', permission_required('event.delete_manager', login_url='login')(views.ManagerDelete.as_view()), name='delete_manager'),

    path('event/ecommerce_app', com_views.index, name='checkout'),
]
