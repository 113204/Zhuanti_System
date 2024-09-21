import requests
from django.forms import models
from django import forms
from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.conf import settings
import os, openai
from utils.decorators import user_login_required
from views.camera import Posedetect


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


@user_login_required
def profile(request):
    return render(request, 'users-profile.html')


@user_login_required
def appointment(request):
    return render(request, 'appointment.html')


@user_login_required
def record(request):
    return render(request, 'record.html')


# @user_login_required
def development(request):
    return render(request, 'development.html')


@user_login_required
def detect(request):
    pose_detect = Posedetect(request.session)  # 將 session 傳遞到 Posedetect
    counter = pose_detect.counter
    return render(request, 'detect.html', locals())

@user_login_required
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@user_login_required
def detect1(request):
    return StreamingHttpResponse(gen(Posedetect(request.session)),  # 將 session 傳遞到 Posedetect
                                 content_type='multipart/x-mixed-replace; boundary=frame')
def stop_camera(request):
    pose_detect = Posedetect(session=request.session)
    pose_detect.stop() 
    return JsonResponse({'status': '鏡頭已關閉'})


@user_login_required
def video(request):
    return render(request, 'video.html')


# @user_login_required
# def wisdomQA(request):
#     return render(request, 'wisdomQA.html')
openai_api_key = ''
openai.api_key = openai_api_key


@user_login_required
def ask_openai(message):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        # model = "gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a professional fitness coach in Taiwan and are proficient in various fitness-related questions, so you can only reply to fitness-related questions in Traditional Chinese."},
            {"role": "user", "content": message},
        ]
    )
    answer = response.choices[0].message.content.strip()
    return answer


@user_login_required
def wisdomQA(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'wisdomQA.html')
