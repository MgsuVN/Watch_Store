from django.contrib import admin
from django.utils.html import format_html
from .models import Brand, Watch, WatchImage, Cart, CartItem, Profile


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
                ('power_reserve', 'case_diameter'),
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