from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, this is app1 index view!")
def index1(request):
    return HttpResponse("Hello t la khanh dep trai!")