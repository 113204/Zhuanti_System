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

def appointment(request):
    return render(request, 'appointment.html')

def record(request):
    return render(request, 'record.html')

def development(request):
    return render(request, 'development.html')
