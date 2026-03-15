from django import forms
from .models import Watch, Profile


class WatchForm(forms.ModelForm):
    class Meta:
        model = Watch
        fields = ['name', 'price', 'description', 'image', 'brand']


class ProfileForm(forms.ModelForm):
    class Meta:
        model  = Profile
        fields = ['avatar', 'phone', 'address', 'bio']
        widgets = {
            'phone':   forms.TextInput(attrs={'placeholder': 'Nhập số điện thoại...'}),
            'address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Nhập địa chỉ...'}),
            'bio':     forms.Textarea(attrs={'rows': 3, 'placeholder': 'Giới thiệu bản thân...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].required  = False
        self.fields['phone'].required   = False
        self.fields['address'].required = False
        self.fields['bio'].required     = False