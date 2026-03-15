from django.shortcuts import render, redirect
from app1.models import Watch, Profile
from django.contrib.auth.decorators import login_required
from app1.forms import ProfileForm
from django.contrib import messages


def home(request):
    products = Watch.objects.all()
    return render(request, 'home.html', {
        'products': products
    })


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'account/profile.html', {'profile': profile})


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật thông tin thành công')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'account/profile_edit.html', {'form': form})