from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('brand/<slug:slug>/', views.brand_detail, name='brand_detail'),
    path('watch/<slug:slug>/', views.watch_detail, name='watch_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:watch_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]