from django.contrib import admin
from django.utils.html import format_html
from .models import Brand, Watch, WatchImage, Cart, CartItem, Profile
from .models import Order, OrderItem, Notification, create_notification

# ===== BRAND =====
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'brand_image')
    prepopulated_fields = {'slug': ('name',)}

    def brand_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;">', obj.image.url)
        return '-'
    brand_image.short_description = 'Ảnh'


# ===== ẢNH PHỤ (inline) =====
class WatchImageInline(admin.TabularInline):
    model = WatchImage
    extra = 3
    fields = ('image', 'order', 'preview')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:4px;">', obj.image.url)
        return '-'
    preview.short_description = 'Xem trước'


# ===== WATCH =====
@admin.register(Watch)
class WatchAdmin(admin.ModelAdmin):
    list_display = ('watch_image', 'name', 'brand', 'price', 'discount_percent', 'is_sold_out', 'sold_count')
    list_display_links = ('watch_image', 'name')
    list_filter = ('brand', 'is_sold_out', 'gender')
    search_fields = ('name', 'brand__name')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_sold_out',)
    inlines = [WatchImageInline]

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'slug', 'brand', 'image', 'description', 'is_sold_out')
        }),
        ('Giá & Khuyến mãi', {
            'fields': ('price', 'discount_percent')
        }),
        ('Thông số kỹ thuật', {
            'fields': (
                ('gender', 'water_resistance'),
                ('movement', 'glass_material'),
                ('strap_material', 'diameter'),
                ('thickness', 'dial_color'),
                ('series', 'case_diameter'),
                ('case_color', 'dial_shape'),
                ('design_style', 'warranty'),
                'features',
            )
        }),
        ('Thống kê', {
            'fields': ('sold_count',),
        }),
    )

    def watch_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;border-radius:6px;">', obj.image.url)
        return '-'
    watch_image.short_description = 'Ảnh'


# ===== CART =====
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal_display',)

    def subtotal_display(self, obj):
        return f"{obj.subtotal:,} đ"
    subtotal_display.short_description = 'Thành tiền'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'total_display', 'created_at')
    inlines = [CartItemInline]

    def item_count(self, obj):
        return obj.item_count
    item_count.short_description = 'Số SP'

    def total_display(self, obj):
        return f"{obj.total:,} đ"
    total_display.short_description = 'Tổng tiền'


# ===== PROFILE =====
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['id', 'full_name', 'phone', 'total', 'status_badge', 'created_at', 'send_notif_btn']
    list_filter   = ['status', 'payment', 'created_at']
    search_fields = ['full_name', 'phone', 'id']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = []

    # Khi admin lưu order, tự động gửi thông báo nếu status thay đổi
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            old_status = Order.objects.get(pk=obj.pk).status
            super().save_model(request, obj, form, change)
            self._send_status_notification(obj)
        else:
            super().save_model(request, obj, form, change)

    def _send_status_notification(self, order):
        messages_map = {
            'confirmed':  ('order_confirmed', f'✅ Đơn hàng #{order.id} đã được xác nhận',
                           'Chúng tôi đã xác nhận đơn hàng của bạn và đang chuẩn bị hàng.'),
            'shipping':   ('order_shipping',  f'🚚 Đơn hàng #{order.id} đang được vận chuyển',
                           'Đơn hàng của bạn đang trên đường giao đến địa chỉ đã đăng ký.'),
            'delivered':  ('order_delivered', f'🎉 Đơn hàng #{order.id} đã được giao thành công',
                           'Cảm ơn bạn đã mua hàng tại WATCHSTORE.VN! Hãy đánh giá sản phẩm nhé.'),
            'cancelled':  ('order_cancelled', f'❌ Đơn hàng #{order.id} đã bị hủy',
                           'Đơn hàng của bạn đã bị hủy. Liên hệ hotline nếu cần hỗ trợ.'),
        }
        if order.status in messages_map:
            notif_type, title, message = messages_map[order.status]
            # Tránh tạo trùng thông báo
            if not Notification.objects.filter(order=order, notif_type=notif_type).exists():
                create_notification(
                    user=order.user,
                    notif_type=notif_type,
                    title=title,
                    message=message,
                    order=order,
                )

    def status_badge(self, obj):
        colors = {
            'pending':   '#f39200',
            'confirmed': '#1a9e3f',
            'shipping':  '#007bff',
            'delivered': '#28a745',
            'cancelled': '#e60023',
        }
        color = colors.get(obj.status, '#666')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Trạng thái'

    def send_notif_btn(self, obj):
        return format_html(
            '<a href="/admin/app1/order/{}/change/" style="font-size:12px;color:#f39200;">Đổi trạng thái</a>',
            obj.pk
        )
    send_notif_btn.short_description = 'Thông báo'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['user', 'title', 'notif_type', 'is_read', 'created_at']
    list_filter   = ['notif_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    actions = ['mark_as_read', 'send_promo_to_all']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'Đã đánh dấu {queryset.count()} thông báo đã đọc.')
    mark_as_read.short_description = 'Đánh dấu đã đọc'

    def send_promo_to_all(self, request, queryset):
        from django.contrib.auth.models import User
        users = User.objects.filter(is_active=True)
        count = 0
        for user in users:
            create_notification(
                user=user,
                notif_type='promotion',
                title='🔥 Flash Sale đặc biệt hôm nay — Giảm tới 48%!',
                message='Hàng ngàn đồng hồ chính hãng đang được giảm giá sâu. Mua ngay!',
            )
            count += 1
        self.message_user(request, f'Đã gửi thông báo khuyến mãi tới {count} người dùng.')
    send_promo_to_all.short_description = '📢 Gửi khuyến mãi tới tất cả users'