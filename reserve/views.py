# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')
def base(request):
    return render(request, 'base.html')
def destinations(request):
    return render(request, 'destinations.html')
def comments(request):
    return render(request, 'comments.html')
def gallery(request):
    return render(request, 'gallery.html')
def packages(request): 
    return render(request, 'packages.html')
def route(request):
    return render(request, 'route.html')

