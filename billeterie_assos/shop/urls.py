from django.conf.urls import url
from django.urls import path
from . import views



urlpatterns = [
    
    path('shop', views.index_shop, name='index_shop'),
    path('product/<int:product_id>/',
        views.show_product, name='product_detail'),
    path('cart/', views.show_cart, name='show_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('qrcode/', views.qrcode, name='qrcode'),
]
