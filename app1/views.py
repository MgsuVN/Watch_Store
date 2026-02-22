from django.shortcuts import render, redirect, get_object_or_404
from .models import Watch, Brand, Cart, CartItem, WatchImage
from .forms import WatchForm
from django.db.models import F
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages


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


@login_required
def add_to_cart(request, watch_id):
    watch = get_object_or_404(Watch, id=watch_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, watch=watch)
    if not created:
        item.quantity += 1
        item.save()
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
    return redirect('cart')


def add_watch(request):
    if request.method == 'POST':
        form = WatchForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = WatchForm()
    return render(request, 'add_watch.html', {'form': form})