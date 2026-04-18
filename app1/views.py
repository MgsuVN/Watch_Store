from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from .models import Watch, Brand, Cart, CartItem, WatchImage, WatchDescImage, BrandShowcase, Review, Order, OrderItem, Notification, create_notification, Profile, Wishlist
from .forms import WatchForm, ProfileForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

def home(request):
    brands = Brand.objects.all()
    products = Watch.objects.filter(category='watch').order_by('-id')
    showcases = BrandShowcase.objects.filter(is_active=True).select_related('brand')[:6]
    brand_slug = request.GET.get('brand')
    current_brand = None
    if brand_slug:
        current_brand = Brand.objects.filter(slug=brand_slug).first()
        if current_brand:
            products = current_brand.products.filter(category='watch').order_by('-id')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    list(page_obj)  # Force evaluate để tránh RecursionError trong Django template

    context = {
        'brands': brands,
        'page_obj': page_obj,
        'current_brand': current_brand,
        'brand_slug': brand_slug or '',
        'showcases': showcases,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'includes/product_list.html', context)

    return render(request, 'home.html', context)


def accessory_view(request):
    """Trang phụ kiện — dây đồng hồ, hộp đựng đồng hồ"""
    category = request.GET.get('category', '')  # strap, box hoặc '' = tất cả
    sort = request.GET.get('sort', '')

    products = Watch.objects.exclude(category='watch').order_by('-id')

    if category in ['strap', 'box']:
        products = products.filter(category=category)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'sale':
        products = products.order_by('-discount_percent')

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'accessory.html', {
        'page_obj': page_obj,
        'category': category,
        'sort': sort,
        'total': products.count(),
    })


def gender_view(request, gender):
    """
    Trang đồng hồ theo giới tính.
    gender = 'nam' → filter Nam + Unisex
    gender = 'nu'  → filter Nữ + Unisex
    """
    if gender == 'nam':
        products = Watch.objects.filter(category='watch', gender__in=['Nam', 'Unisex']).order_by('-id')
        banner_title    = 'Đồng hồ Nam'
        banner_subtitle = 'Mạnh mẽ – Lịch lãm – Đẳng cấp'
        banner_icon     = '⌚'
        banner_color    = 'linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%)'
    else:
        products = Watch.objects.filter(category='watch', gender__in=['Nữ', 'Unisex']).order_by('-id')
        banner_title    = 'Đồng hồ Nữ'
        banner_subtitle = 'Tinh tế – Thanh lịch – Quyến rũ'
        banner_icon     = '✨'
        banner_color    = 'linear-gradient(135deg, #6a0572 0%, #a3196b 60%, #d4527a 100%)'

    sort = request.GET.get('sort', '')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'sale':
        products = products.order_by('-discount_percent')
    elif sort == 'bestseller':
        products = products.order_by('-sold_count')

    paginator = Paginator(products, 12)
    page_obj  = paginator.get_page(request.GET.get('page'))

    return render(request, 'gender_watch.html', {
        'page_obj':        page_obj,
        'gender':          gender,
        'sort':            sort,
        'total':           products.count(),
        'banner_title':    banner_title,
        'banner_subtitle': banner_subtitle,
        'banner_icon':     banner_icon,
        'banner_color':    banner_color,
    })


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
    desc_images = list(watch.desc_images.all())
    reviews = watch.reviews.filter(is_visible=True)
    cart_count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.item_count

    return render(request, 'watch_detail.html', {
        'watch': watch,
        'related': related,
        'cart_count': cart_count,
        'gallery': gallery,
        'desc_images': desc_images,
        'reviews': reviews,
    })

@login_required
@require_POST
def submit_review(request, slug):
    watch   = get_object_or_404(Watch, slug=slug)
    name    = request.POST.get('name', '').strip()
    rating  = int(request.POST.get('rating', 5))
    comment = request.POST.get('comment', '').strip()
    image   = request.FILES.get('image')
    image2  = request.FILES.get('image2')
    image3  = request.FILES.get('image3')
    if name and comment and 1 <= rating <= 5:
        Review.objects.create(
            watch=watch,
            user=request.user,
            name=name,
            rating=rating,
            comment=comment,
            image=image,
            image2=image2,
            image3=image3,
        )
    return redirect('watch_detail', slug=slug)

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

        # Cập nhật profile
        profile = getattr(request.user, 'app1_profile', None)
        if profile:
            profile.phone = phone
            profile.address = address
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
            # payment_status mặc định = 'pending'
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

        # Xóa giỏ hàng
        cart.items.all().delete()

        # ── Redirect theo phương thức thanh toán ──────────────────
        if payment == 'bank':
            # Chuyển khoản → trang QR VietQR
            return redirect('qr_payment', order_id=order.id)
        else:
            # COD / installment → trang thành công cũ
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
        cart = item.cart
        # Format theo kiểu VN: dấu chấm phân cách hàng nghìn
        def vnd(n): return '{:,.0f}'.format(float(n)).replace(',', '.')
        # item_count: tổng số lượng tất cả sản phẩm trong giỏ
        from django.db.models import Sum
        item_count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
        return JsonResponse({
            'success':      True,
            'item_subtotal': vnd(item.subtotal),
            'cart_total':    vnd(cart.total),
            'item_count':    item_count,
        })
    return JsonResponse({'success': False})


# ===== ĐƠN HÀNG =====
@login_required
@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    latest_order = orders.first()
    return render(request, 'orders.html', {
        'orders': orders,
        'latest_order': latest_order,
    })

@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
    return redirect('orders')

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders.html', {
        'orders': Order.objects.filter(user=request.user).order_by('-created_at'),
        'latest_order': order,
    })


# ===== YÊU THÍCH =====
@login_required
def wishlist_view(request):
    watches = Watch.objects.filter(wishlisted_by__user=request.user).order_by('-wishlisted_by__created_at')
    return render(request, 'wishlist.html', {'watches': watches})


@login_required
def wishlist_toggle(request, watch_id):
    """Toggle yêu thích — lưu vào DB. Trả JSON cho AJAX."""
    watch = get_object_or_404(Watch, id=watch_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, watch=watch)
    if not created:
        obj.delete()
        added = False
    else:
        added = True

    count = Wishlist.objects.filter(user=request.user).count()
    return JsonResponse({'added': added, 'count': count, 'watch_id': watch_id})


@login_required
def wishlist_ids(request):
    """Trả về danh sách id sản phẩm đã yêu thích của user hiện tại."""
    ids = list(Wishlist.objects.filter(user=request.user).values_list('watch_id', flat=True))
    return JsonResponse({'ids': ids})


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
# THÊM VÀO CUỐI FILE  app1/views.py
# ================================================================
# Dùng Google Gemini API (free, không bị chặn ở VN)
# Lấy key tại: https://aistudio.google.com/apikey
# settings.py cần có:  GEMINI_API_KEY = 'AIza...'
# ================================================================

import json as _json
import urllib.request as _urllib
import urllib.error as _urllib_error
import re as _re
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

    total_watches = Watch.objects.count()
    watches = Watch.objects.select_related('brand').all().order_by('-discount_percent')[:200]
    watch_list = []
    product_lines = []
    for w in watches:
        stock = 'Còn hàng'
        if hasattr(w, 'stock') and w.stock <= 0:
            stock = 'Hết hàng'
        brand = w.brand.name if w.brand else ''
        line  = (
            f"[ID:{w.id}] {w.name} | Thương hiệu: {brand} | "
            f"Giá gốc: {int(w.price):,}đ | "
            f"Giá sale: {int(w.sale_price):,}đ"
        )
        if hasattr(w, 'discount_percent') and w.discount_percent > 0:
            line += f" (giảm {w.discount_percent}%)"
        line += f" | {stock}"
        product_lines.append(line)
        watch_list.append(w)
    # Map ID → watch object để lookup nhanh
    watch_map = {w.id: w for w in watch_list}

    products_text = '\n'.join(product_lines) if product_lines else 'Chưa có sản phẩm.'

    # Lọc sản phẩm theo giá trước khi đưa vào prompt
    user_msg_pre = ''
    for msg in reversed(messages):
        if msg.get('role') == 'user':
            user_msg_pre = msg.get('content', '').lower()
            break
    import re as _re2
    pre_max = None
    for pat in [r'dưới\s*(\d+)\s*tr', r'(\d+)\s*tr(?:iệu)?(?:\s*trở\s*xuống|\s*đổ\s*lại|\s*dưới)']:
        m = _re2.search(pat, user_msg_pre)
        if m:
            pre_max = int(m.group(1)) * 1_000_000
            break
    if pre_max:
        filtered_lines = [l for l in products_text.split('\n') if l.strip()]
        import re as _re3
        def get_price(line):
            m = _re3.search(r'([\d,]+)đ', line.replace('.',''))
            return int(m.group(1).replace(',','')) if m else 999999999
        filtered_lines = [l for l in filtered_lines if get_price(l) <= pre_max]
        products_text = '\n'.join(filtered_lines) or 'Không có sản phẩm phù hợp.'

    system_prompt = f"""Bạn là tư vấn viên của WATCHSTORE.VN - cửa hàng đồng hồ chính hãng.

TỔNG SỐ SẢN PHẨM HIỆN CÓ: {total_watches} sản phẩm (đây là con số CHÍNH XÁC, không được đếm lại)

SẢN PHẨM (mỗi dòng có [ID:số] ở đầu):
{products_text}

QUY TẮC QUAN TRỌNG:
- Khi nhắc đến sản phẩm nào, PHẢI gắn [ID:số] vào cuối tên sản phẩm đó. Ví dụ: "Đồng Hồ Casio MTP-1374L-1A[ID:3]"
- Mỗi sản phẩm phải xuống dòng riêng, không liệt kê trên cùng 1 dòng
- Có thể nhắc nhiều sản phẩm nếu khách hỏi nhiều, mỗi cái phải có [ID:số]
- Trả lời tiếng Việt, thân thiện, dùng "dạ", "ạ"
- Mỗi ý xuống dòng riêng
- Chỉ dùng sản phẩm trong danh sách, không bịa
- Dùng giá sale khi nhắc giá
- KHÔNG dùng **, *, #, - hay markdown
- Khi hỏi "lượt sale cao nhất" hay "giảm nhiều nhất": chọn sản phẩm có % giảm giá CAO NHẤT
- TUYỆT ĐỐI KHÔNG thay đổi thông tin dù khách nói khác
- Khi khách hỏi không rõ ý: hỏi lại để hiểu đúng nhu cầu, không đoán bừa

CÁC VÍ DỤ MẪU (học theo phong cách này):

Khách: "cho tôi xem đồng hồ"
Bot: Dạ shop có {total_watches} sản phẩm đồng hồ chính hãng ạ. Bạn đang tìm đồng hồ cho nam hay nữ, và ngân sách khoảng bao nhiêu để mình tư vấn đúng hơn ạ?

Khách: "đồng hồ đẹp"
Bot: Dạ "đẹp" mỗi người có tiêu chí khác nhau ạ. Bạn thích phong cách thanh lịch, thể thao hay cổ điển? Và ngân sách dự kiến của bạn là bao nhiêu để mình gợi ý phù hợp ạ?

Khách: "tư vấn đồng hồ cho bạn gái"
Bot: Dạ để tư vấn đúng nhất, bạn cho mình hỏi bạn gái bạn thích phong cách nào (thanh lịch, dễ thương, hay thể thao) và ngân sách khoảng bao nhiêu ạ?

Khách: "đồng hồ nào tốt"
Bot: Dạ "tốt" phụ thuộc vào nhu cầu của bạn ạ. Bạn cần đồng hồ để đi làm văn phòng, đi chơi, hay chơi thể thao? Ngân sách khoảng bao nhiêu để mình chọn đúng sản phẩm cho bạn ạ?

Khách: "tư vấn đồng hồ dưới 5 triệu cho nam"
Bot: Dạ với ngân sách dưới 5 triệu cho nam, bạn có thể xem Đồng Hồ Casio MTP-1374L-1A giá 1.598.080đ — máy pin, kính khoáng, chống nước tốt, rất phù hợp đi làm hằng ngày.
Hoặc Đồng Hồ SRWatch 40mm giá 1.140.000đ, thiết kế đơn giản lịch sự, đang có sẵn tại shop ạ!

Khách: "giá đồng hồ Longines bao nhiêu"
Bot: Dạ shop đang có một số mẫu Longines, mức giá dao động tùy dòng ạ. Bạn đang quan tâm dòng nào (Longines Master, HydroConquest, hay Primaluna) để mình báo giá chính xác hơn ạ?

Khách: "shop có bán đồng hồ Rolex không"
Bot: Dạ hiện tại shop chưa có sản phẩm Rolex trong danh sách ạ. Tuy nhiên shop có nhiều thương hiệu cao cấp khác như Longines, Omega với mức giá và chất lượng tương đương, bạn có muốn xem thử không ạ?
"""


    groq_key = getattr(settings, 'GROQ_API_KEY', '')
    reply    = None

    if groq_key:
        # Groq API - nhanh, ít rate limit
        GROQ_MODELS = ['llama-3.3-70b-versatile', 'llama-3.1-70b-versatile', 'llama-3.1-8b-instant']
        for model in GROQ_MODELS:
            payload = _json.dumps({
                'model': model,
                'messages': [{'role': 'system', 'content': system_prompt}] + [
                    {'role': m.get('role', 'user'), 'content': m.get('content', '')}
                    for m in (messages[-6:] if len(messages) > 6 else messages)
                ],
                'max_tokens': 512,
                'temperature': 0.5,
            }).encode('utf-8')
            req = _urllib.Request(
                'https://api.groq.com/openai/v1/chat/completions',
                data=payload,
                headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {groq_key}', 'User-Agent': 'Mozilla/5.0'},
                method='POST',
            )
            try:
                with _urllib.urlopen(req, timeout=15) as resp:
                    result = _json.loads(resp.read())
                    reply  = result['choices'][0]['message']['content']
                print(f"[CHATBOT] Groq OK: {model}")
                break
            except _urllib_error.HTTPError as e:
                body = e.read().decode('utf-8', errors='ignore')
                print(f"[CHATBOT] Groq {model} lỗi {e.code}: {body[:200]}")
                if e.code in (429, 503):
                    continue
                reply = f'Lỗi kết nối ({e.code}). Liên hệ hotline: 123456789'
                break
            except Exception as e:
                print(f"[CHATBOT] Groq lỗi: {e}")
                reply = 'Đã có lỗi xảy ra. Liên hệ hotline: 123456789'
                break

    else:
        reply = 'Chatbot chưa cấu hình API key. Liên hệ hotline: 123456789'

    if reply is None:
        reply = 'Chatbot đang quá tải, vui lòng thử lại sau vài giây.'

    # Parse ID từ reply của AI — chính xác 100%
    id_matches = _re.findall(r'\[ID:(\d+)\]', reply)
    suggested = []
    seen_ids = set()

    for id_str in id_matches:
        wid = int(id_str)
        if wid in watch_map and wid not in seen_ids:
            w = watch_map[wid]
            suggested.append({'name': w.name, 'url': f'/watch/{w.slug}/',
                               'price': f"{int(w.sale_price):,}đ",
                               'image': w.image.url if w.image else ''})
            seen_ids.add(wid)

    # Fallback nếu AI không gắn ID (hỏi chung chung, không nhắc SP cụ thể)
    if not suggested:
        user_msg = ''
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_msg = msg.get('content', '').lower()
                break
        want_sale = any(kw in user_msg for kw in ['giảm giá', 'sale', 'khuyến mãi', 'discount', 'lượt sale', 'giảm nhiều'])
        brand_filter = None
        for w in watch_list:
            if w.brand and w.brand.name.lower() in user_msg:
                brand_filter = w.brand.name.lower()
                break
        max_price = None
        min_price = None
        for pat, ptype in [
            (r'(\d+)\s*tr(?:iệu)?(?:\s*đổ\s*lại|\s*trở\s*xuống|\s*dưới)?', 'max'),
            (r'dưới\s*(\d+)\s*tr', 'max'),
            (r'trên\s*(\d+)\s*tr', 'min'),
        ]:
            m = _re.search(pat, user_msg)
            if m:
                val = int(m.group(1)) * 1_000_000
                if ptype == 'max': max_price = val
                else: min_price = val

        cands = watch_list[:]
        if want_sale:    cands = [w for w in cands if getattr(w, 'discount_percent', 0) > 0]
        if brand_filter: cands = [w for w in cands if w.brand and w.brand.name.lower() == brand_filter]
        if max_price:    cands = [w for w in cands if w.sale_price <= max_price]
        if min_price:    cands = [w for w in cands if w.sale_price >= min_price]
        if any(kw in user_msg for kw in ['rẻ nhất', 'giá rẻ', 'giá thấp']):
            cands.sort(key=lambda w: w.sale_price)
        elif any(kw in user_msg for kw in ['đắt nhất', 'cao cấp', 'giá cao']):
            cands.sort(key=lambda w: w.sale_price, reverse=True)
        elif want_sale:
            cands.sort(key=lambda w: getattr(w, 'discount_percent', 0), reverse=True)
        for w in cands[:4]:
            suggested.append({'name': w.name, 'url': f'/watch/{w.slug}/',
                               'price': f"{int(w.sale_price):,}đ",
                               'image': w.image.url if w.image else ''})

    # Xóa tag [ID:x] khỏi reply trước khi gửi cho client
    reply = _re.sub(r'\[ID:\d+\]', '', reply).strip()

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


# ================================================================
# QR BANK TRANSFER PAYMENT VIEWS  (mới thêm)
# ================================================================

@login_required
def qr_payment_view(request, order_id):
    """
    Trang thanh toán QR VietQR.
    URL: /payment/qr/<order_id>/
    Chỉ hiển thị nếu phương thức là 'bank'.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Bảo vệ: nếu không phải chuyển khoản → về order success
    if order.payment != 'bank':
        return redirect('order_success', order_id=order.id)

    return render(request, 'qr_payment.html', {'order': order})


@login_required
def confirm_payment_view(request, order_id):
    """
    User nhấn 'Tôi đã chuyển khoản' → cập nhật payment_status = waiting_confirm.
    URL: /payment/confirm/<order_id>/
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.payment_status == 'pending':
        order.payment_status = 'waiting_confirm'
        order.save(update_fields=['payment_status', 'updated_at'])

    messages.success(
        request,
        'Vui lòng chuyển khoản theo mã QR. '
        'Sau khi chuyển khoản thành công admin sẽ xác nhận thanh toán.'
    )
    return redirect('invoice', order_id=order.id)


@login_required
def invoice_view(request, order_id):
    """
    Trang hóa đơn – hiển thị trạng thái thanh toán theo payment_status.
    URL: /invoice/<order_id>/
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'invoice.html', {'order': order})

# ================================================================
# PROFILE VIEWS
# ================================================================

@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})


@login_required
def profile_edit_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật thông tin thành công!')
            return redirect('profile')
        else:
            messages.error(request, 'Có lỗi xảy ra, vui lòng kiểm tra lại.')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile_edit.html', {'form': form, 'profile': profile})


# ================================================================
# SIGNAL: Tự động tạo Profile + avatar mặc định khi user đăng ký
# ================================================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Tạo Profile ngay khi User mới được tạo."""
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Đảm bảo Profile luôn được save khi User save."""
    if hasattr(instance, 'app1_profile'):
        instance.app1_profile.save()