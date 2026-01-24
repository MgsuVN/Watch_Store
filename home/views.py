from django.shortcuts import render
def home(request): # Đổi từ get_home thành home
    return render(request, 'home.html')