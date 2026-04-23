from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Sum, Q
from django.contrib.auth.models import User

import json
import datetime

from .models import Brand, Watch, WatchImage, WatchDescImage, BrandShowcase, Review, Cart, CartItem, Profile,Refund
from .models import Order, OrderItem, Notification, create_notification


# ================================================================
# BRAND
# ================================================================
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'brand_image')
    prepopulated_fields = {'slug': ('name',)}

    def brand_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;">', obj.image.url)
        return '-'
    brand_image.short_description = 'Ảnh'


# ================================================================
# WATCH (chỉ hiện Đồng Hồ — category='watch')
# ================================================================
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

class WatchDescImageInline(admin.TabularInline):
    model = WatchDescImage
    extra = 2
    max_num = 10
    fields = ('image', 'layout', 'caption', 'order', 'preview')
    readonly_fields = ('preview',)
    verbose_name        = 'Ảnh mô tả chi tiết'
    verbose_name_plural = 'Ảnh mô tả chi tiết (tối đa 10 ảnh)'

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:80px;border-radius:4px;">', obj.image.url)
        return '-'
    preview.short_description = 'Xem trước'

@admin.register(BrandShowcase)
class BrandShowcaseAdmin(admin.ModelAdmin):
    list_display  = ('brand', 'order', 'is_active', 'poster_preview')
    list_editable = ('order', 'is_active')
    ordering      = ('order',)

    def poster_preview(self, obj):
        if obj.poster:
            return format_html('<img src="{}" style="height:60px;border-radius:6px;">', obj.poster.url)
        return '-'
    poster_preview.short_description = 'Poster'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display   = ('name', 'watch', 'rating', 'is_visible', 'created_at', 'short_comment', 'image_preview')
    list_editable  = ('is_visible',)
    list_filter    = ('rating', 'is_visible', 'created_at')
    search_fields  = ('name', 'comment', 'watch__name')
    readonly_fields = ('name', 'watch', 'user', 'rating', 'comment', 'image', 'image_preview', 'created_at')
    ordering       = ('-created_at',)

    def short_comment(self, obj):
        return obj.comment[:60] + '...' if len(obj.comment) > 60 else obj.comment
    short_comment.short_description = 'Nội dung'

    def image_preview(self, obj):
        html = ''
        for img in [obj.image, obj.image2, obj.image3]:
            if img:
                html += f'<img src="{img.url}" style="height:60px;border-radius:6px;margin-right:4px;">'
        return mark_safe(html) if html else '-'
    image_preview.short_description = 'Ảnh'

    def has_add_permission(self, request):
        return False

@admin.register(Watch)
class WatchAdmin(admin.ModelAdmin):
    list_display = ('watch_image', 'name', 'brand', 'category', 'price', 'discount_percent', 'is_sold_out', 'sold_count')
    list_display_links = ('watch_image', 'name')
    list_filter = ('category', 'brand', 'is_sold_out', 'gender')
    search_fields = ('name', 'brand__name')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_sold_out', 'category')
    inlines = [WatchImageInline, WatchDescImageInline]

    def get_queryset(self, request):
        # Bảng Đồng Hồ chỉ hiển thị category='watch'
        return super().get_queryset(request).filter(category='watch')

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('category', 'name', 'slug', 'brand', 'image', 'description', 'is_sold_out')
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


# ================================================================
# PHỤ KIỆN (Proxy Admin — lọc strap + box từ bảng Watch)
# ================================================================
class AccessoryProxy(Watch):
    """Proxy model để tạo mục riêng 'Phụ Kiện' trên admin sidebar."""
    class Meta:
        proxy = True
        verbose_name        = 'Phụ kiện'
        verbose_name_plural = 'Phụ kiện (Dây & Hộp)'

@admin.register(AccessoryProxy)
class AccessoryAdmin(admin.ModelAdmin):
    list_display       = ('accessory_image', 'name', 'category_badge', 'brand', 'price', 'discount_percent', 'is_sold_out')
    list_display_links = ('accessory_image', 'name')
    list_filter        = ('category', 'brand', 'is_sold_out')
    search_fields      = ('name', 'brand__name')
    prepopulated_fields = {'slug': ('name',)}
    list_editable      = ('is_sold_out',)
    inlines            = [WatchImageInline, WatchDescImageInline]

    def get_queryset(self, request):
        # Chỉ hiện dây (strap) và hộp (box)
        return super().get_queryset(request).filter(category__in=['strap', 'box'])

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Giới hạn dropdown category chỉ còn strap & box
        if 'category' in form.base_fields:
            form.base_fields['category'].choices = [
                ('strap', 'Dây Đồng Hồ'),
                ('box',   'Hộp Đựng Đồng Hồ'),
            ]
        return form

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('category', 'name', 'slug', 'brand', 'image', 'description', 'is_sold_out')
        }),
        ('Giá & Khuyến mãi', {
            'fields': ('price', 'discount_percent')
        }),
        ('Thông số', {
            'fields': ('strap_material', 'diameter', 'warranty', 'features'),
        }),
        ('Thống kê', {
            'fields': ('sold_count',),
        }),
    )

    def accessory_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;border-radius:6px;">', obj.image.url)
        return '-'
    accessory_image.short_description = 'Ảnh'

    def category_badge(self, obj):
        color = '#1565c0' if obj.category == 'strap' else '#6d4c41'
        label = obj.get_category_display()
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:10px;font-size:12px;">{}</span>',
            color, label
        )
    category_badge.short_description = 'Loại'


# ================================================================
# CART
# ================================================================
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


# ================================================================
# PROFILE
# ================================================================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')


# ================================================================
# ORDER  (duy nhất — đã tích hợp payment_status)
# ================================================================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('watch_name', 'price', 'quantity', 'subtotal')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display   = [
        'id', 'full_name', 'phone', 'total_display',
        'payment_badge', 'payment_status_badge',
        'status_badge', 'created_at', 'send_notif_btn',
    ]
    list_filter    = ['status', 'payment_status', 'payment', 'created_at']
    search_fields  = ['full_name', 'phone', 'id']
    readonly_fields = ['created_at', 'updated_at']
    list_editable  = []
    inlines        = [OrderItemInline]
    actions        = ['mark_payment_waiting', 'mark_payment_paid', 'mark_payment_pending']

    fieldsets = (
        ('Thông tin khách hàng', {
            'fields': ('user', 'full_name', 'phone', 'address', 'city', 'note')
        }),
        ('Đơn hàng', {
            'fields': ('payment', 'total', 'status')
        }),
        ('✅ Trạng thái thanh toán QR', {
            'fields': ('payment_status',),
            'description': (
                '⏳ pending = chờ thanh toán  |  '
                '🔍 waiting_confirm = khách đã chuyển khoản, chờ admin xác nhận  |  '
                '✅ paid = đã xác nhận thanh toán thành công'
            ),
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    # ── Actions để đổi payment_status hàng loạt ───────────────────
    def mark_payment_paid(self, request, queryset):
        updated = queryset.update(payment_status='paid')
        self.message_user(request, f'✅ Đã xác nhận thanh toán cho {updated} đơn hàng.')
    mark_payment_paid.short_description = '✅ Xác nhận đã thanh toán (paid)'

    def mark_payment_waiting(self, request, queryset):
        updated = queryset.update(payment_status='waiting_confirm')
        self.message_user(request, f'🔍 Đã chuyển {updated} đơn sang "Chờ xác nhận".')
    mark_payment_waiting.short_description = '🔍 Chuyển sang Chờ xác nhận'

    def mark_payment_pending(self, request, queryset):
        updated = queryset.update(payment_status='pending')
        self.message_user(request, f'⏳ Đã reset {updated} đơn về "Chờ thanh toán".')
    mark_payment_pending.short_description = '⏳ Reset về Chờ thanh toán'

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            super().save_model(request, obj, form, change)
            self._send_status_notification(obj)
        else:
            super().save_model(request, obj, form, change)

    def _send_status_notification(self, order):
        messages_map = {
            'confirmed': (
                'order_confirmed',
                f' Đơn hàng #{order.id} đã được xác nhận',
                'Chúng tôi đã xác nhận đơn hàng của bạn và đang chuẩn bị hàng.',
            ),
            'shipping': (
                'order_shipping',
                f' Đơn hàng #{order.id} đang được vận chuyển',
                'Đơn hàng của bạn đang trên đường giao đến địa chỉ đã đăng ký.',
            ),
            'delivered': (
                'order_delivered',
                f' Đơn hàng #{order.id} đã giao thành công',
                'Cảm ơn bạn đã mua hàng tại WATCHSTORE.VN! Hãy đánh giá sản phẩm nhé.',
            ),
            'cancelled': (
                'order_cancelled',
                f' Đơn hàng #{order.id} đã bị hủy',
                'Đơn hàng của bạn đã bị hủy. Liên hệ hotline nếu cần hỗ trợ.',
            ),
        }
        if order.status in messages_map:
            notif_type, title, message = messages_map[order.status]
            if not Notification.objects.filter(order=order, notif_type=notif_type).exists():
                create_notification(
                    user=order.user, notif_type=notif_type,
                    title=title, message=message, order=order,
                )

    # ── Cột hiển thị ──────────────────────────────────────────────
    def total_display(self, obj):
        formatted = f"{int(obj.total):,} đ"
        return format_html('<strong style="color:#e60023;">{}</strong>', formatted)
    total_display.short_description = 'Tổng tiền'
    total_display.admin_order_field = 'total'

    def payment_badge(self, obj):
        icons = {'bank': '💳', 'cod': '🚚', 'installment': '📆'}
        labels = {'bank': 'Chuyển khoản', 'cod': 'COD', 'installment': 'Fundiin'}
        return format_html(
            '<span style="font-size:12px;">{} {}</span>',
            icons.get(obj.payment, ''), labels.get(obj.payment, obj.payment)
        )
    payment_badge.short_description = 'Thanh toán'

    def payment_status_badge(self, obj):
        cfg = {
            'pending':         ('#f39200', '⏳ Chờ TT'),
            'waiting_confirm': ('#1565c0', '🔍 Chờ xác nhận'),
            'paid':            ('#1a9e3f', '✅ Đã TT'),
            'refunded':        ('#7c3aed', '↩️ Đã hoàn tiền'),
        }
        color, label = cfg.get(obj.payment_status, ('#888', obj.payment_status))
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;'
            'border-radius:12px;font-size:12px;white-space:nowrap;">{}</span>',
            color, label
        )
    payment_status_badge.short_description = 'TT Thanh toán'

    def status_badge(self, obj):
        colors = {
            'pending': '#f39200', 'confirmed': '#1a9e3f',
            'shipping': '#007bff', 'delivered': '#28a745', 'cancelled': '#e60023',
        }
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:12px;">{}</span>',
            colors.get(obj.status, '#666'), obj.get_status_display()
        )
    status_badge.short_description = 'Trạng thái ĐH'

    def send_notif_btn(self, obj):
        return format_html(
            '<a href="/admin/app1/order/{}/change/" style="font-size:12px;color:#f39200;">Đổi trạng thái</a>',
            obj.pk
        )
    send_notif_btn.short_description = 'Thao tác'


# ================================================================
# NOTIFICATION
# ================================================================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display   = ['user', 'title', 'notif_type', 'is_read', 'created_at']
    list_filter    = ['notif_type', 'is_read', 'created_at']
    search_fields  = ['user__username', 'title']
    list_editable  = ['is_read']
    readonly_fields = ['created_at']
    actions = ['mark_as_read', 'send_promo_to_all']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'Đã đánh dấu {queryset.count()} thông báo đã đọc.')
    mark_as_read.short_description = 'Đánh dấu đã đọc'

    def send_promo_to_all(self, request, queryset):
        users = User.objects.filter(is_active=True)
        count = 0
        for user in users:
            create_notification(
                user=user, notif_type='promotion',
                title='🔥 Flash Sale đặc biệt hôm nay — Giảm tới 48%!',
                message='Hàng ngàn đồng hồ chính hãng đang được giảm giá sâu. Mua ngay!',
            )
            count += 1
        self.message_user(request, f'Đã gửi thông báo khuyến mãi tới {count} người dùng.')
    send_promo_to_all.short_description = '📢 Gửi khuyến mãi tới tất cả users'


# ================================================================
# DASHBOARD THỐNG KÊ — override trang chủ Jazzmin Admin
# ================================================================
def get_dashboard_stats(request):
    now   = timezone.now()
    today = now.date()

    period    = request.GET.get('period', 'month')
    date_from = request.GET.get('date_from', '')
    date_to   = request.GET.get('date_to', '')

    if date_from and date_to:
        try:
            df = datetime.date.fromisoformat(date_from)
            dt = datetime.date.fromisoformat(date_to)
            qs_filter    = Q(created_at__date__gte=df, created_at__date__lte=dt)
            period_label = f"{df.strftime('%d/%m/%Y')} – {dt.strftime('%d/%m/%Y')}"
            period = 'custom'
        except ValueError:
            qs_filter    = Q()
            period_label = 'Tất cả'
    elif period == 'today':
        qs_filter    = Q(created_at__date=today)
        period_label = 'Hôm nay'
    elif period == 'week':
        qs_filter    = Q(created_at__date__gte=today - datetime.timedelta(days=7))
        period_label = '7 ngày qua'
    elif period == 'year':
        qs_filter    = Q(created_at__year=now.year)
        period_label = f'Năm {now.year}'
    elif period == 'all':
        qs_filter    = Q()
        period_label = 'Tất cả thời gian'
    else:
        qs_filter    = Q(created_at__year=now.year, created_at__month=now.month)
        period_label = f'Tháng {now.month}/{now.year}'

    orders_qs = Order.objects.filter(qs_filter).exclude(status='cancelled')

    def fmt_vnd(v):
        v = int(v or 0)
        if v >= 1_000_000_000: return f"{v/1_000_000_000:.1f} tỷ đ"
        if v >= 1_000_000:     return f"{v/1_000_000:.1f}M đ"
        return f"{v:,} đ"

    revenue = orders_qs.aggregate(t=Sum('total'))['t'] or 0

    status_map = {
        'pending':   'Chờ xác nhận',
        'confirmed': 'Đã xác nhận',
        'shipping':  'Đang giao',
        'delivered': 'Đã giao',
        'cancelled': 'Đã hủy',
    }

    daily_labels, daily_data = [], []
    for i in range(29, -1, -1):
        d   = today - datetime.timedelta(days=i)
        rev = Order.objects.filter(created_at__date=d).exclude(status='cancelled') \
                           .aggregate(t=Sum('total'))['t'] or 0
        daily_labels.append(d.strftime('%d/%m'))
        daily_data.append(int(rev))

    monthly_labels, monthly_data = [], []
    for i in range(11, -1, -1):
        m, y = now.month - i, now.year
        while m <= 0:
            m += 12
            y -= 1
        rev = Order.objects.filter(created_at__year=y, created_at__month=m) \
                           .exclude(status='cancelled').aggregate(t=Sum('total'))['t'] or 0
        monthly_labels.append(f'T{m}/{y}')
        monthly_data.append(int(rev))

    brand_stats = (
        OrderItem.objects
        .filter(order__in=Order.objects.exclude(status='cancelled'))
        .values('watch__brand__name')
        .annotate(rev=Sum('subtotal'))
        .order_by('-rev')[:8]
    )

    top_raw = (
        OrderItem.objects.filter(order__in=orders_qs)
        .values('watch_name')
        .annotate(total_qty=Sum('quantity'), revenue=Sum('subtotal'))
        .order_by('-total_qty')[:8]
    )

    recent_raw = Order.objects.order_by('-created_at')[:8]

    return {
        'revenue_display':  fmt_vnd(revenue),
        'total_orders':     Order.objects.filter(qs_filter).count(),
        'completed_orders': Order.objects.filter(qs_filter, status='delivered').count(),
        'pending_orders':   Order.objects.filter(qs_filter, status='pending').count(),
        'total_products':   Watch.objects.count(),
        'sold_out_count':   Watch.objects.filter(is_sold_out=True).count(),
        'total_users':      User.objects.filter(is_staff=False).count(),
        'new_users_month':  User.objects.filter(
            date_joined__year=now.year,
            date_joined__month=now.month,
            is_staff=False,
        ).count(),
        'period':        period,
        'period_label':  period_label,
        'date_from':     date_from,
        'date_to':       date_to,
        'daily_labels':  json.dumps(daily_labels),
        'daily_data':    json.dumps(daily_data),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data':  json.dumps(monthly_data),
        'brand_labels':  json.dumps([b['watch__brand__name'] or 'Khác' for b in brand_stats]),
        'brand_data':    json.dumps([int(b['rev'] or 0) for b in brand_stats]),
        'status_labels': json.dumps(list(status_map.values())),
        'status_data':   json.dumps([Order.objects.filter(status=k).count() for k in status_map]),
        'top_products':  [
            {
                'watch_name':      t['watch_name'],
                'total_qty':       t['total_qty'],
                'revenue_display': fmt_vnd(t['revenue'] or 0),
            }
            for t in top_raw
        ],
        'recent_orders': [
            {
                'id':                 o.id,
                'full_name':          o.full_name,
                'total_display':      fmt_vnd(o.total),
                'status':             o.status,
                'get_status_display': o.get_status_display(),
            }
            for o in recent_raw
        ],
    }

def revenue_view(request):
    context = dict(
        admin.site.each_context(request),
        **get_dashboard_stats(request)
    )
    return TemplateResponse(request, "admin/revenue.html", context)


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):

    list_display  = (
        'order_link', 'user', 'bank_name', 'bank_account',
        'account_holder', 'status_badge', 'status', 'created_at',
    )
    list_filter   = ('status', 'created_at')
    search_fields = ('order__id', 'user__username', 'user__email',
                     'bank_name', 'bank_account')
    ordering      = ('-created_at',)
    list_editable = ('status',)

    readonly_fields = (
        'order', 'user', 'bank_name', 'bank_account',
        'account_holder', 'reason', 'created_at',
    )

    fieldsets = (
        ('📋 Thông tin đơn hàng', {
            'fields': ('order', 'user', 'created_at'),
        }),
        ('🏦 Thông tin ngân hàng', {
            'fields': ('bank_name', 'bank_account', 'account_holder'),
        }),
        ('📝 Lý do yêu cầu', {
            'fields': ('reason',),
        }),
        ('⚙️ Xử lý hoàn tiền', {
            'fields': ('status', 'completed_at'),
            'description': (
                '⚠️ Đổi <strong>Trạng thái</strong> thành <strong>completed</strong> '
                'rồi nhấn Lưu → hệ thống tự gửi thông báo cho khách.'
            ),
        }),
    )

    actions = ['mark_as_completed']

    @admin.action(description='✅ Đánh dấu hoàn tiền thành công')
    def mark_as_completed(self, request, queryset):
        done = 0
        for refund in queryset.filter(status='pending'):
            refund.status = 'approved'
            refund.completed_at = timezone.now()
            refund.save(update_fields=['status', 'completed_at'])

            Order.objects.filter(pk=refund.order.pk).update(payment_status='refunded')

            create_notification(
                user=refund.user,
                notif_type='general',
                title=f'Hoàn tiền đơn #{refund.order.id} thành công ✅',
                message=(
                    f'Đơn hàng #{refund.order.id} đã được hoàn tiền thành công. '
                    'Tiền sẽ về tài khoản của bạn trong 24h.'
                ),
                order=refund.order,
            )
            done += 1
        self.message_user(request, f'✅ {done} yêu cầu đã được xác nhận hoàn tiền.')

    def save_model(self, request, obj, form, change):
        # Lấy trạng thái cũ từ DB
        try:
            old_status = Refund.objects.get(pk=obj.pk).status
        except Refund.DoesNotExist:
            old_status = None

        just_approved = (old_status != 'approved' and obj.status == 'approved')
        just_rejected = (old_status != 'rejected' and obj.status == 'rejected')

        # Tự set completed_at khi chuyển sang approved
        if just_approved:
            obj.completed_at = timezone.now()

        # Luôn save refund trước
        obj.save()

        # Khi vừa approved: cập nhật order + gửi thông báo
        if just_approved:
            Order.objects.filter(pk=obj.order.pk).update(payment_status='refunded')
            create_notification(
                user=obj.user,
                notif_type='general',
                title=f'Hoàn tiền đơn #{obj.order.id} thành công ✅',
                message=(
                    f'Đơn hàng #{obj.order.id} đã được hoàn tiền thành công. '
                    'Tiền sẽ về tài khoản của bạn trong 24h.'
                ),
                order=obj.order,
            )
            self.message_user(request, '✅ Đã xác nhận hoàn tiền và gửi thông báo cho khách.')

        # Khi vừa rejected: gửi thông báo từ chối
        if just_rejected:
            create_notification(
                user=obj.user,
                notif_type='general',
                title=f'Yêu cầu hoàn tiền đơn #{obj.order.id} bị từ chối ❌',
                message=f'Yêu cầu hoàn tiền cho đơn #{obj.order.id} đã bị từ chối.',
                order=obj.order,
            )
            self.message_user(request, '❌ Đã từ chối hoàn tiền và gửi thông báo cho khách.')

    @admin.display(description='Đơn hàng', ordering='order__id')
    def order_link(self, obj):
        url = f'/admin/app1/order/{obj.order.id}/change/'
        return format_html('<a href="{}">Đơn #{}</a>', url, obj.order.id)

    @admin.display(description='Trạng thái')
    def status_badge(self, obj):
        if obj.status == 'pending':
            color, label = '#f97316', '⏳ Chờ xử lý'
        elif obj.status == 'approved':
            color, label = '#22c55e', '✅ Đã hoàn tiền'
        else:  # rejected
            color, label = '#ef4444', '❌ Từ chối hoàn tiền'
        return format_html(
            '<span style="color:{};font-weight:700;">{}</span>',
            color, label,
        )


# ── Thêm URL doanh thu vào admin site (đặt sau tất cả register) ───
def get_admin_urls(urls):
    def get_urls():
        my_urls = [
            path('doanh-thu/', admin.site.admin_view(revenue_view), name="doanh_thu"),
        ]
        return my_urls + urls
    return get_urls

admin.site.get_urls = get_admin_urls(admin.site.get_urls())