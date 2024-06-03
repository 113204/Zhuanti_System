import requests
from django.forms import models
from django import forms
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os


def index(request):
    return render(request, 'index.html')


def test(request):
    # user = models.User.objects.all()
    # return render(request, 'test.html', {"User": user})
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


def detect(request):
    return render(request, 'detect.html')


def wisdomQA(request):
    return render(request, 'wisdomQA.html')

def favicon(request):
    favicon_path = os.path.join(settings.STATIC_ROOT, 'favicon.ico')
    with open(favicon_path, 'rb') as f:
        return HttpResponse(f.read(), content_type='image/vnd.microsoft.icon')