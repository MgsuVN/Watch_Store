from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Watch
from .forms import WatchForm

def home(request):
    watches = Watch.objects.all().order_by('-id')
    return render(request, 'home.html', {'watches': watches})

def add_watch(request):
    if request.method == 'POST':
        form = WatchForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = WatchForm()

    return render(request, 'add_watch.html', {'form': form})
