from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.conf import settings

class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='brands/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


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
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def sale_price(self):
        if self.discount_percent > 0:
            return int(self.price * (1 - self.discount_percent / 100))
        return self.price

    def __str__(self):
        return self.name


# ===== ẢNH PHỤ SẢN PHẨM =====
class WatchImage(models.Model):
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE, related_name='extra_images')
    image = models.ImageField(upload_to='products/gallery/')
    order = models.IntegerField(default=0, verbose_name='Thứ tự')

    class Meta:
        ordering = ['order']
        verbose_name = 'Ảnh sản phẩm'
        verbose_name_plural = 'Ảnh sản phẩm'

    def __str__(self):
        return f"Ảnh #{self.order} - {self.watch.name}"


# ===== GIỎ HÀNG =====
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return self.items.count()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    @property
    def subtotal(self):
        return self.watch.sale_price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.watch.name}"


# ===== PROFILE =====
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='app1_profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
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

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Đơn hàng'

    def __str__(self):
        return f'Đơn #{self.id} - {self.full_name}'


class OrderItem(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    watch      = models.ForeignKey('Watch', on_delete=models.SET_NULL, null=True, blank=True)
    watch_name = models.CharField(max_length=300)
    price      = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    quantity   = models.PositiveIntegerField(default=1)
    subtotal   = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    class Meta:
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Chi tiết đơn hàng'

    def __str__(self):
        return f'{self.watch_name} x{self.quantity}'
# ================================================================
# THÊM ĐOẠN NÀY VÀO CUỐI models.py (sau class OrderItem)
# ================================================================

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


# ================================================================
# HÀM TIỆN ÍCH — dùng trong views.py để tạo thông báo nhanh
# ================================================================
def create_notification(user, notif_type, title, message='', order=None):
    """Tạo thông báo cho user"""
    return Notification.objects.create(
        user=user,
        notif_type=notif_type,
        title=title,
        message=message,
        order=order,
    )