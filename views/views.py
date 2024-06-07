import requests
from django.forms import models
from django import forms
from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
from django.conf import settings
import os
from utils.decorators import user_login_required


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

@user_login_required
def record(request):
    return render(request, 'record.html')


def development(request):
    return render(request, 'development.html')


@user_login_required
def detect(request):
    return render(request, 'detect.html')

@user_login_required
def wisdomQA(request):
    return render(request, 'wisdomQA.html')
