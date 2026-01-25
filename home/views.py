from django.shortcuts import render
from app1.models import Watch   # 👈 sửa ở đây

def home(request):
    products = Watch.objects.all()
    return render(request, 'home.html', {
        'products': products
    })
