from django.shortcuts import render, redirect, get_object_or_404
from .models import Watch, Brand, Cart, CartItem, WatchImage, Order, OrderItem, Notification, create_notification
from .forms import WatchForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings

def home(request):
    brands = Brand.objects.all()
    products = Watch.objects.all().order_by('-id')

    brand_slug = request.GET.get('brand')
    current_brand = None
    if brand_slug:
        current_brand = Brand.objects.filter(slug=brand_slug).first()
        if current_brand:
            products = current_brand.products.all().order_by('-id')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'brands': brands,
        'page_obj': page_obj,
        'current_brand': current_brand,
        'brand_slug': brand_slug or '',
    }

    if request.headers.get('HX-Request'):
        return render(request, 'includes/product_list.html', context)

    return render(request, 'home.html', context)


def brand_detail(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    products = brand.products.all()

    min_price = request.GET.get('min')
    max_price = request.GET.get('max')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort = request.GET.get('sort')
    if sort == "price_asc":
        products = products.order_by('price')
    elif sort == "price_desc":
        products = products.order_by('-price')
    elif sort == "sale":
        products = products.order_by('-discount_percent')
    elif sort == "bestseller":
        products = products.order_by('-sold_count')
    else:
        products = products.order_by('-id')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'brand_detail.html', {
        'brand': brand,
        'page_obj': page_obj,
    })


def watch_detail(request, slug):
    watch = get_object_or_404(Watch, slug=slug)
    related = Watch.objects.filter(brand=watch.brand).exclude(id=watch.id)[:4]
    gallery = list(watch.extra_images.all())

    cart_count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.item_count

    return render(request, 'watch_detail.html', {
        'watch': watch,
        'related': related,
        'cart_count': cart_count,
        'gallery': gallery,
    })


# ===== TÌM KIẾM =====
def search_view(request):
    q = request.GET.get('q', '').strip()
    results = Watch.objects.none()
    if q:
        results = Watch.objects.filter(name__icontains=q).order_by('-id')

    paginator = Paginator(results, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'search_results.html', {
        'q': q,
        'page_obj': page_obj,
        'total': results.count(),
    })


def search_ajax(request):
    q = request.GET.get('q', '').strip()
    ids_param = request.GET.get('ids', '').strip()
    results = []

    # Lấy theo danh sách ids (cho trang wishlist)
    if ids_param:
        try:
            ids = [int(i) for i in ids_param.split(',') if i.strip().isdigit()]
            watches = Watch.objects.filter(id__in=ids)
            for w in watches:
                results.append({
                    'id': w.id,
                    'name': w.name,
                    'url': f'/watch/{w.slug}/',
                    'image': w.image.url if w.image else '',
                    'price': f"{w.sale_price:,} đ",
                })
        except Exception:
            pass
    # Tìm kiếm theo tên
    elif len(q) >= 2:
        watches = Watch.objects.filter(name__icontains=q)[:6]
        for w in watches:
            results.append({
                'id': w.id,
                'name': w.name,
                'url': f'/watch/{w.slug}/',
                'image': w.image.url if w.image else '',
                'price': f"{w.sale_price:,} đ",
            })
    return JsonResponse({'results': results})


# ===== GIỎ HÀNG =====
@login_required
def add_to_cart(request, watch_id):
    watch = get_object_or_404(Watch, id=watch_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, watch=watch)

    # Trả về JSON nếu là AJAX request (hiệu ứng bay)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if created:
            msg = f'Đã thêm "{watch.name}" vào giỏ hàng!'
            status = 'added'
        else:
            item.quantity += 1
            item.save()
            msg = f'"{watch.name}" đã có trong giỏ! Số lượng: {item.quantity}'
            status = 'updated'
        return JsonResponse({
            'status': status,
            'message': msg,
            'cart_count': cart.item_count,
        })

    if not created:
        item.quantity += 1
        item.save()
        messages.warning(request, f'"{watch.name}" đã có trong giỏ! Số lượng: {item.quantity}')
    else:
        messages.success(request, f'Đã thêm "{watch.name}" vào giỏ hàng!')
    return redirect('watch_detail', slug=watch.slug)


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart.html', {'cart': cart})


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    # Nếu là AJAX request (từ checkout page) → trả JSON, không redirect
    if request.headers.get('Content-Type') == 'application/json' or \
       request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('cart')


# ===== CHECKOUT =====
@login_required
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        return redirect('cart')

    total_saved = sum(
        (item.watch.price - item.watch.sale_price) * item.quantity
        for item in cart.items.all()
        if item.watch.discount_percent > 0
    )

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '')
        phone    = request.POST.get('phone', '')
        address  = request.POST.get('address', '')
        city     = request.POST.get('city', '')
        payment  = request.POST.get('payment', 'cod')
        note     = request.POST.get('note', '')

        if not all([full_name, phone, address, city]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin giao hàng!')
            return redirect('checkout')

        # Lưu vào profile nếu chưa có
        profile = getattr(request.user, 'app1_profile', None)
        if profile:
            if not profile.phone: profile.phone = phone
            if not profile.address: profile.address = address
            profile.save()

        # Tạo đơn hàng
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            city=city,
            note=note,
            payment=payment,
            total=cart.total,
        )

        # Tạo các order item từ giỏ hàng
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                watch=item.watch,
                watch_name=item.watch.name,
                price=item.watch.sale_price,
                quantity=item.quantity,
                subtotal=item.subtotal,
            )

        # Xóa giỏ hàng sau khi đặt hàng
        cart.items.all().delete()

        messages.success(request, f'Đặt hàng thành công! Cảm ơn {full_name} đã mua hàng tại WATCHSTORE.VN! Mã đơn: #{order.id}')
        return redirect('order_success', order_id=order.id)
        

    return render(request, 'checkout.html', {
        'cart': cart,
        'total_saved': total_saved,
    })


@login_required
def update_cart_item(request, item_id):
    import json
    if request.method == 'POST':
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        data = json.loads(request.body)
        qty = int(data.get('quantity', 1))
        if qty < 1: qty = 1
        item.quantity = qty
        item.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


# ===== ĐƠN HÀNG =====
@login_required
def orders_view(request):
    return render(request, 'orders.html', {})


# ===== YÊU THÍCH =====
@login_required
def wishlist_view(request):
    wishlist_ids = request.session.get('wishlist', [])
    watches = Watch.objects.filter(id__in=wishlist_ids)
    return render(request, 'wishlist.html', {'watches': watches})


@login_required
def wishlist_toggle(request, watch_id):
    wishlist = request.session.get('wishlist', [])
    if watch_id in wishlist:
        wishlist.remove(watch_id)
        added = False
    else:
        wishlist.append(watch_id)
        added = True
    request.session['wishlist'] = wishlist
    request.session.modified = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'added': added, 'count': len(wishlist)})
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def add_watch(request):
    if request.method == 'POST':
        form = WatchForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = WatchForm()
    return render(request, 'add_watch.html', {'form': form})
# ================================================================
# ================================================================
# THÊM VÀO CUỐI FILE  app1/views.py
# ================================================================
# Dùng Google Gemini API (free, không bị chặn ở VN)
# Lấy key tại: https://aistudio.google.com/apikey
# settings.py cần có:  GEMINI_API_KEY = 'AIza...'
# ================================================================

import json as _json
import urllib.request as _urllib
import urllib.error as _urllib_error
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


# ===== CHATBOT =====
@require_POST
def chatbot_view(request):
    try:
        data     = _json.loads(request.body)
        messages = data.get('messages', [])
    except Exception:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    # ── Lấy sản phẩm từ database ──────────────────────────────
    watches = Watch.objects.select_related('brand').all()[:200]
    watch_list = []  # lưu để so khớp sau
    product_lines = []
    for w in watches:
        stock = 'Còn hàng'
        if hasattr(w, 'stock') and w.stock <= 0:
            stock = 'Hết hàng'
        brand = w.brand.name if w.brand else ''
        line  = (
            f"- {w.name} | Thương hiệu: {brand} | "
            f"Giá gốc: {int(w.price):,}đ | "
            f"Giá sale: {int(w.sale_price):,}đ"
        )
        if hasattr(w, 'discount_percent') and w.discount_percent > 0:
            line += f" (giảm {w.discount_percent}%)"
        line += f" | {stock}"
        product_lines.append(line)
        watch_list.append(w)

    products_text = '\n'.join(product_lines) if product_lines else 'Chưa có sản phẩm.'

    system_prompt = f"""Bạn là trợ lý tư vấn bán hàng của WATCHSTORE.VN – cửa hàng đồng hồ chính hãng.

DANH SÁCH SẢN PHẨM HIỆN TẠI:
{products_text}

QUY TẮC:
- Trả lời tiếng Việt, thân thiện, ngắn gọn
- Chỉ dùng dữ liệu từ danh sách trên, không bịa thêm
- Nếu hỏi giá: dùng giá sale (giá bán thực tế)
- Nếu không tìm thấy sản phẩm: gợi ý sản phẩm tương tự
- Khi đề cập sản phẩm cụ thể, hãy viết ĐÚNG tên sản phẩm như trong danh sách
- Hotline: 093 189 2222"""

    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        return JsonResponse({'reply': 'Chatbot chưa cấu hình API key. Liên hệ hotline: 093 189 2222'})

    # ── Chuyển messages sang format Gemini ────────────────────
    gemini_contents = []
    for msg in messages:
        role    = 'model' if msg.get('role') == 'assistant' else 'user'
        content = msg.get('content', '').strip()
        if content:
            gemini_contents.append({
                'role': role,
                'parts': [{'text': content}]
            })

    # Tin nhắn cuối phải là 'user'
    if gemini_contents and gemini_contents[-1]['role'] == 'model':
        gemini_contents.pop()
    if not gemini_contents:
        gemini_contents = [{'role': 'user', 'parts': [{'text': 'Xin chào'}]}]

    payload = _json.dumps({
        'contents': gemini_contents,
        'system_instruction': {
            'parts': [{'text': system_prompt}]
        },
        'generationConfig': {
            'maxOutputTokens': 1000,
            'temperature': 0.7,
        }
    }).encode('utf-8')

    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
    req = _urllib.Request(
        url,
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    try:
        with _urllib.urlopen(req, timeout=30) as resp:
            result = _json.loads(resp.read())
            reply  = result['candidates'][0]['content']['parts'][0]['text']

    except _urllib_error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')
        print(f"--- CHI TIẾT LỖI TỪ GOOGLE ---\n{body}\n-------------------------------")
        reply = f'Lỗi API ({e.code}). Kiểm tra lại API Key hoặc liên hệ hotline: 093 189 2222'

    except _urllib_error.URLError as e:
        print(f"[CHATBOT] URLError: {e.reason}")
        reply = 'Không thể kết nối đến máy chủ Google. Vui lòng thử lại sau.'

    except Exception as e:
        print(f"[CHATBOT] Lỗi không xác định: {e}")
        reply = 'Đã có lỗi xảy ra. Vui lòng liên hệ hotline: 093 189 2222'

    # ── So khớp sản phẩm: ưu tiên reply, bổ sung từ câu hỏi ──
    import re as _re

    # Lấy câu hỏi cuối của user
    user_msg = ''
    for msg in reversed(messages):
        if msg.get('role') == 'user':
            user_msg = msg.get('content', '').lower()
            break

    reply_lower = reply.lower()
    suggested = []
    seen_ids = set()

    # Phát hiện lọc theo giá từ câu hỏi user
    max_price = None
    min_price = None
    price_patterns = [
        (r'(\d+)\s*tr(?:iệu)?(?:\s*đổ\s*lại|\s*trở\s*xuống|\s*dưới)?', 'max'),
        (r'dưới\s*(\d+)\s*tr', 'max'),
        (r'trên\s*(\d+)\s*tr', 'min'),
        (r'từ\s*(\d+)\s*tr', 'min'),
    ]
    for pattern, ptype in price_patterns:
        m = _re.search(pattern, user_msg)
        if m:
            val = int(m.group(1)) * 1_000_000
            if ptype == 'max':
                max_price = val
            else:
                min_price = val

    # Phát hiện lọc theo thương hiệu
    brand_filter = None
    for w in watch_list:
        if w.brand and w.brand.name.lower() in user_msg:
            brand_filter = w.brand.name.lower()
            break

    # Phát hiện lọc giảm giá
    want_sale = any(kw in user_msg for kw in ['giảm giá', 'sale', 'khuyến mãi', 'discount'])

    # Bước 1: match tên sản phẩm trong reply
    for w in watch_list:
        if w.id not in seen_ids and w.name.lower() in reply_lower:
            suggested.append({
                'name': w.name,
                'url': f'/watch/{w.slug}/',
                'price': f"{int(w.sale_price):,}đ",
                'image': w.image.url if w.image else '',
            })
            seen_ids.add(w.id)
            if len(suggested) >= 4:
                break

    # Bước 2: nếu chưa đủ 4, bổ sung theo filter từ câu hỏi
    if len(suggested) < 4:
        candidates = watch_list[:]
        if want_sale:
            candidates = [w for w in candidates if hasattr(w, 'discount_percent') and w.discount_percent > 0]
        if brand_filter:
            candidates = [w for w in candidates if w.brand and w.brand.name.lower() == brand_filter]
        if max_price:
            candidates = [w for w in candidates if w.sale_price <= max_price]
        if min_price:
            candidates = [w for w in candidates if w.sale_price >= min_price]

        # Sắp xếp: giảm giá cao nhất trước, nếu không thì rẻ nhất trước
        if want_sale:
            candidates.sort(key=lambda w: getattr(w, 'discount_percent', 0), reverse=True)
        elif max_price:
            candidates.sort(key=lambda w: w.sale_price, reverse=True)

        for w in candidates:
            if w.id not in seen_ids:
                suggested.append({
                    'name': w.name,
                    'url': f'/watch/{w.slug}/',
                    'price': f"{int(w.sale_price):,}đ",
                    'image': w.image.url if w.image else '',
                })
                seen_ids.add(w.id)
                if len(suggested) >= 4:
                    break

    return JsonResponse({'reply': reply, 'suggested_products': suggested})
@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_success.html', {'order': order})

# ================================================================
# NOTIFICATION VIEWS
# ================================================================

@login_required
def notification_list(request):
    """API: trả về danh sách thông báo dạng JSON cho header"""
    notifs = Notification.objects.filter(user=request.user)[:20]
    data = [{
        'id':         n.id,
        'type':       n.notif_type,
        'icon':       n.icon,
        'icon_class': n.icon_class,
        'title':      n.title,
        'message':    n.message,
        'is_read':    n.is_read,
        'time':       _time_ago(n.created_at),
        'order_id':   n.order_id,
    } for n in notifs]

    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'notifications': data, 'unread_count': unread_count})


@login_required
def notification_mark_read(request, notif_id=None):
    """Đánh dấu 1 hoặc tất cả thông báo đã đọc"""
    if request.method == 'POST':
        if notif_id:
            Notification.objects.filter(id=notif_id, user=request.user).update(is_read=True)
        else:
            # Đánh dấu tất cả
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({'ok': True, 'unread_count': unread_count})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def _time_ago(dt):
    """Chuyển datetime thành chuỗi '2 phút trước'"""
    from django.utils import timezone
    now = timezone.now()
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return 'Vừa xong'
    elif seconds < 3600:
        return f'{seconds // 60} phút trước'
    elif seconds < 86400:
        return f'{seconds // 3600} giờ trước'
    elif seconds < 604800:
        return f'{seconds // 86400} ngày trước'
    else:
        return dt.strftime('%d/%m/%Y')