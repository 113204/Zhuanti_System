import requests
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def test(request):
    return render(request, 'test.html')


def login(request):
    return render(request, 'pages-login.html')


def register(request):
    return render(request, 'pages-register.html')


def profile(request):
    return render(request, 'users-profile.html')
