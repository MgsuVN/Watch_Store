from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_watch, name='add_watch'),
]
