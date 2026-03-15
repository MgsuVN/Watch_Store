from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.conf import settings


# ── Thương hiệu đồng hồ ──────────────────────────────────────
class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='brands/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Tự động tạo slug từ tên nếu chưa có
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ── Sản phẩm đồng hồ ─────────────────────────────────────────
class Watch(models.Model):
    # ===== THÔNG TIN CƠ BẢN =====
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name='products',
        null=True, blank=True
    )
    price = models.IntegerField()
    discount_percent = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)
    is_sold_out = models.BooleanField(default=False)

    # ===== THÔNG SỐ KỸ THUẬT =====
    gender = models.CharField(
        max_length=10,
        choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Unisex', 'Unisex')],
        blank=True,
        verbose_name='Đối tượng'
    )
    water_resistance = models.CharField(max_length=50, blank=True, verbose_name='Chống nước')
    movement = models.CharField(max_length=100, blank=True, verbose_name='Loại máy')
    glass_material = models.CharField(max_length=100, blank=True, verbose_name='Chất liệu kính')
    strap_material = models.CharField(max_length=100, blank=True, verbose_name='Chất liệu dây')
    diameter = models.CharField(max_length=50, blank=True, verbose_name='Size mặt')
    thickness = models.CharField(max_length=50, blank=True, verbose_name='Độ dày')
    dial_color = models.CharField(max_length=100, blank=True, verbose_name='Màu mặt')
    series = models.CharField(max_length=100, blank=True, verbose_name='Series')
    case_diameter = models.CharField(max_length=100, blank=True, verbose_name='Đường kính mặt')
    case_color = models.CharField(max_length=100, blank=True, verbose_name='Màu vỏ')
    dial_shape = models.CharField(max_length=100, blank=True, verbose_name='Hình dáng mặt')
    design_style = models.CharField(max_length=100, blank=True, verbose_name='Kiểu thiết kế')
    features = models.TextField(blank=True, verbose_name='Tiện ích')
    warranty = models.CharField(max_length=100, blank=True, default='24 tháng', verbose_name='Bảo hành')

    # ===== META =====
    sold_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        # Tự động tạo slug từ tên nếu chưa có
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def sale_price(self):
        """Tính giá sau khi giảm. Nếu không giảm thì trả về giá gốc."""
        if self.discount_percent > 0:
            return int(self.price * (1 - self.discount_percent / 100))
        return self.price

    def __str__(self):
        return self.name


# ── Ảnh phụ của sản phẩm (gallery) ──────────────────────────
class WatchImage(models.Model):
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE, related_name='extra_images')
    image = models.ImageField(upload_to='products/gallery/')
    order = models.IntegerField(default=0, verbose_name='Thứ tự')
class WatchDescImage(models.Model):
    """Ảnh minh hoạ trong phần mô tả chi tiết sản phẩm (quản lý từ admin)."""

    LAYOUT_CHOICES = [
        ('full',        '📷 Ảnh toàn chiều rộng'),
        ('float_left',  '◧ Ảnh trái — chữ bên phải'),
        ('float_right', '◨ Ảnh phải — chữ bên trái'),
    ]

    watch   = models.ForeignKey(Watch, on_delete=models.CASCADE, related_name='desc_images')
    image   = models.ImageField(upload_to='watch_desc/', blank=True, null=True, help_text='Không bắt buộc — để trống nếu chỉ cần thêm chữ')
    caption = models.TextField(blank=True, help_text='Đoạn chữ hiển thị bên cạnh ảnh (chỉ dùng khi chọn layout trái/phải)')
    layout  = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='full', help_text='Kiểu hiển thị')
    order   = models.PositiveIntegerField(default=0, help_text='Thứ tự hiển thị (số nhỏ hiện trước)')


    class Meta:
        ordering = ['order']
        verbose_name        = 'Ảnh mô tả'
        verbose_name_plural = 'Ảnh mô tả sản phẩm'

    def __str__(self):
        return f"Ảnh mô tả #{self.order} — {self.watch.name}"
    class Meta:
        ordering = ['order']
        verbose_name = 'Ảnh sản phẩm'
        verbose_name_plural = 'Ảnh sản phẩm'

    def __str__(self):
        return f"Ảnh #{self.order} - {self.watch.name}"


# ── Giỏ hàng (mỗi user có 1 giỏ duy nhất) ───────────────────
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total(self):
        """Tổng tiền tất cả sản phẩm trong giỏ."""
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        """Số lượng loại sản phẩm trong giỏ."""
        return self.items.count()


# ── Từng sản phẩm trong giỏ hàng ─────────────────────────────
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    @property
    def subtotal(self):
        """Thành tiền = giá sale × số lượng."""
        return self.watch.sale_price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.watch.name}"


# ── Thông tin mở rộng của user ────────────────────────────────
# Tự động tạo khi User mới được tạo (qua signal post_save)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='app1_profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Profile: {self.user.username}"

    @property
    def avatar_color(self):
        """Màu nền avatar mặc định theo chữ cái đầu username."""
        colors = ['#f39200', '#e60023', '#1565c0', '#1a9e3f',
                  '#8b5cf6', '#06b6d4', '#f97316', '#ec4899']
        initial = self.user.username[0].upper() if self.user.username else 'U'
        return colors[ord(initial) % len(colors)]

    @property
    def avatar_initial(self):
        """Chữ cái đầu để hiển thị trong avatar mặc định."""
        return self.user.username[0].upper() if self.user.username else 'U'


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Signal: tự động tạo Profile khi User mới được tạo."""
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)


# ── Đơn hàng ─────────────────────────────────────────────────
class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cod',         'Thanh toán khi nhận hàng'),
        ('bank',        'Chuyển khoản ngân hàng'),
        ('installment', 'Trả sau cùng Fundiin'),
    ]

    STATUS_CHOICES = [
        ('pending',    'Chờ xác nhận'),
        ('confirmed',  'Đã xác nhận'),
        ('shipping',   'Đang giao hàng'),
        ('delivered',  'Đã giao hàng'),
        ('cancelled',  'Đã hủy'),
    ]

    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    full_name  = models.CharField(max_length=200)
    phone      = models.CharField(max_length=20)
    address    = models.TextField()
    city       = models.CharField(max_length=100)
    note       = models.TextField(blank=True, default='')
    payment    = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total      = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_status = models.CharField(
    max_length=20,
    choices=[('pending','Chờ thanh toán'), ('waiting_confirm','Chờ xác nhận'), ('paid','Đã thanh toán')],
    default='pending',
)
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Đơn hàng'

    def __str__(self):
        return f'Đơn #{self.id} - {self.full_name}'


# ── Từng sản phẩm trong đơn hàng ─────────────────────────────
# Lưu lại tên & giá tại thời điểm đặt, tránh mất dữ liệu khi
# sản phẩm bị xóa hoặc thay đổi giá sau này
class OrderItem(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    watch      = models.ForeignKey('Watch', on_delete=models.SET_NULL, null=True, blank=True)
    watch_name = models.CharField(max_length=300)   # tên tại thời điểm đặt
    price      = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    quantity   = models.PositiveIntegerField(default=1)
    subtotal   = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    class Meta:
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Chi tiết đơn hàng'

    def __str__(self):
        return f'{self.watch_name} x{self.quantity}'


# ── Thông báo cho user ────────────────────────────────────────
class Notification(models.Model):
    NOTIF_TYPES = [
        ('order_placed',    '📦 Đặt hàng thành công'),
        ('order_confirmed', '✅ Đơn hàng đã xác nhận'),
        ('order_shipping',  '🚚 Đang vận chuyển'),
        ('order_delivered', '🎉 Đã giao hàng'),
        ('order_cancelled', '❌ Đơn hàng đã hủy'),
        ('promotion',       '🔥 Khuyến mãi'),
        ('general',         'ℹ️ Thông báo chung'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=30, choices=NOTIF_TYPES, default='general')
    title      = models.CharField(max_length=255)
    message    = models.TextField(blank=True)
    order      = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Thông báo'
        verbose_name_plural = 'Thông báo'

    def __str__(self):
        return f"[{self.user.username}] {self.title}"

    @property
    def icon(self):
        """Trả về emoji icon theo loại thông báo."""
        icons = {
            'order_placed':    '📦',
            'order_confirmed': '✅',
            'order_shipping':  '🚚',
            'order_delivered': '🎉',
            'order_cancelled': '❌',
            'promotion':       '🔥',
            'general':         'ℹ️',
        }
        return icons.get(self.notif_type, 'ℹ️')

    @property
    def icon_class(self):
        """Trả về CSS class theo loại thông báo."""
        classes = {
            'order_placed':    'order',
            'order_confirmed': 'order',
            'order_shipping':  'order',
            'order_delivered': 'order',
            'order_cancelled': 'danger',
            'promotion':       'sale',
            'general':         'info',
        }
        return classes.get(self.notif_type, 'info')


# ── Hàm tiện ích ──────────────────────────────────────────────
def create_notification(user, notif_type, title, message='', order=None):
    """Tạo thông báo cho user. Gọi từ views.py sau các sự kiện quan trọng."""
    return Notification.objects.create(
        user=user,
        notif_type=notif_type,
        title=title,
        message=message,
        order=order,
    )
class BrandShowcase(models.Model):
    """Hãng nổi bật hiển thị trên trang chủ."""
    brand  = models.OneToOneField(Brand, on_delete=models.CASCADE, related_name='showcase')
    poster = models.ImageField(upload_to='showcase/', help_text='Ảnh poster bên trái')
    order  = models.PositiveIntegerField(default=0, help_text='Thứ tự hiển thị (số nhỏ lên trước)')
    is_active = models.BooleanField(default=True, help_text='Bật/tắt hiển thị')

    class Meta:
        ordering = ['order']
        verbose_name        = 'Hãng nổi bật'
        verbose_name_plural = 'Hãng nổi bật trang chủ'

    def __str__(self):
        return f"{self.brand.name} (thứ tự {self.order})"
class Review(models.Model):
    watch      = models.ForeignKey(Watch, on_delete=models.CASCADE, related_name='reviews')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='reviews')
    name       = models.CharField(max_length=100)
    rating     = models.PositiveSmallIntegerField(default=5)
    comment    = models.TextField()
    image      = models.ImageField(upload_to='reviews/', blank=True, null=True)
    image2     = models.ImageField(upload_to='reviews/', blank=True, null=True) 
    image3     = models.ImageField(upload_to='reviews/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=True, help_text='Bật/tắt hiển thị đánh giá này')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.watch.name} ({self.rating}★)"


# ── Thương hiệu đồng hồ ──────────────────────────────────────