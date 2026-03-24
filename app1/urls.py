from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('phu-kien/', views.accessory_view, name='accessory'),
    path('nam/', views.gender_view, {'gender': 'nam'}, name='watch_nam'),
    path('nu/', views.gender_view, {'gender': 'nu'}, name='watch_nu'),
    path('brand/<slug:slug>/', views.brand_detail, name='brand_detail'),
    path('watch/<slug:slug>/', views.watch_detail, name='watch_detail'),
    path('watch/<slug:slug>/review/', views.submit_review, name='submit_review'),
    # Tìm kiếm
    path('search/', views.search_view, name='search'),
    path('search/ajax/', views.search_ajax, name='search_ajax'),

    # Giỏ hàng
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:watch_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),

    # Thanh toán
    path('checkout/', views.checkout_view, name='checkout'),

    # Đơn hàng
    path('orders/', views.orders_view, name='orders'),
    path('orders/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('orders/success/<int:order_id>/', views.order_success_view, name='order_success'),
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    # Yêu thích
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:watch_id>/', views.wishlist_toggle, name='wishlist_toggle'),
    path('wishlist/ids/', views.wishlist_ids, name='wishlist_ids'),

    # Chat bot
    path('chatbot/', views.chatbot_view, name='chatbot'),

    # Thông báo
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/read/', views.notification_mark_read, name='notification_mark_all'),
    path('notifications/read/<int:notif_id>/', views.notification_mark_read, name='notification_mark_read'),

    # QR
    path('payment/qr/<int:order_id>/',      views.qr_payment_view,       name='qr_payment'),
    path('payment/confirm/<int:order_id>/', views.confirm_payment_view,  name='confirm_payment'),
    path('invoice/<int:order_id>/',         views.invoice_view,           name='invoice'),

    # Profile
    path('profile/',      views.profile_view,      name='profile'),
    path('profile/edit/', views.profile_edit_view,  name='profile_edit'),
]