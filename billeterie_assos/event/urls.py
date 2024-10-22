from django.urls import path
from django.contrib.auth.decorators import login_required, permission_required
from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin
from social_django.urls import urlpatterns as social_django_urls
from shop import views as com_views
from . import views

app_name = 'event'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('assos/mine/', login_required(views.MyAssosView.as_view(), login_url='login'), name='my_assos'),
    url(r'^admin/', admin.site.urls),
    url(r'', include('cri_epita.urls', namespace="cri")),
    path('assos/<int:pk>', views.AssosDetailView.as_view(), name='asso_detail'),
    path('assos/', views.AssosView.as_view(), name='assos'),
    path('event/', views.EventListView.as_view(), name='events'),
    path('event/<int:pk>', views.EventDetailView.as_view(), name='event_detail'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('upcomming_events/', views.Upcomming_Events, name='upcomming_events'),
    path('assos/delete/<int:pk>', views.AssosDelete.as_view(), name='assos_delete'),
    path('assos/<int:asso_pk>/delete/member/<int:pk>', views.MemberDelete.as_view(), name='delete_member'),
    path('assos/<int:asso_pk>/manager/add/<int:pk>', views.ManagerCreate.as_view(), name='add_manager'),
    path('assos/<int:asso_pk>/delete/manager/<int:pk>', views.ManagerDelete.as_view(), name='delete_manager'),
    path('shop/', com_views.index_shop, name='shop'),
    path('product/<int:product_id>/', com_views.show_product, name='product_detail'),
    path('search/', views.search, name='search'),
    path('assos/create/', permission_required('event.add_association', login_url='login')(views.AssosCreateView.as_view()), name='asso_creation'),
    path('assos/event/create/', views.EventCreateGeneralView.as_view(), name='general_event_creation'),
    path('assos/event/create/<int:asso>', views.EventCreateView.as_view(), name='event_creation'),
    path('event/delete/<int:pk>', views.EventDelete.as_view(), name='event_delete'),
    path('event/cancelable/<int:pk>', views.EventCancelable.as_view(), name='make_cancelable'),
    path('event/cancel/<int:pk>', views.EventCancel.as_view(), name='event_cancel'),
    path('assos/president/add/<int:pk>', permission_required('event.add_president', login_url='login')(views.PresidentCreate.as_view()), name='add_president'),
    path('event/<int:event_pk>/staff/delete/<int:pk>', views.StaffDelete.as_view(), name='staff_delete'),
    path('event/approve/<int:pk>', views.EventApprove.as_view(), name='event_approve'),
    path('event/validate/<int:pk>', views.EventValidate.as_view(), name='event_validate'),
    path('event/pending/<int:pk>', views.EventDisapprove.as_view(), name='event_disapprove'),
    path('dashboard/', views.DashBoard.as_view(), name='dashboard'),
]
