from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('brand/<slug:slug>/', views.brand_detail, name='brand_detail'),
    path('watch/<slug:slug>/', views.watch_detail, name='watch_detail'),

    # Tìm kiếm
    path('search/', views.search_view, name='search'),
    path('search/ajax/', views.search_ajax, name='search_ajax'),

    # Giỏ hàng
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:watch_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),  # ← THÊM

    # Thanh toán
    path('checkout/', views.checkout_view, name='checkout'),  # ← THÊM

    # Đơn hàng
    path('orders/', views.orders_view, name='orders'),

    # Yêu thích
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:watch_id>/', views.wishlist_toggle, name='wishlist_toggle'),

    # Chat bot
    path('chatbot/', views.chatbot_view, name='chatbot'),
]