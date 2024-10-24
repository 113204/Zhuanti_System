import requests,re
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

def privacypolicies(request):
    return render(request, 'privacypolicies.html')


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


# @user_login_required
def video(request):
    return render(request, 'video.html')


# @user_login_required
# def wisdomQA(request):
#     return render(request, 'wisdomQA.html')
openai_api_key = ''
openai.api_key = openai_api_key


# @user_login_required
def ask_openai(message):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        # model = "gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a professional fitness coach in Taiwan and are proficient in various fitness-related questions, so you can only reply to fitness-related questions in Traditional Chinese."},
            {"role": "user", "content": message},
        ],
        temperature=1,
        top_p=0.9

    )
    # 獲取回覆內容
    answer = response.choices[0].message.content.strip()

    # 使用正則表達式替換所有的粗體和三級標題
    answer = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', answer)  # 替換粗體
    answer = re.sub(r'### (.*?)\n', r'<h3>\1</h3>\n', answer)  # 替換三級標題

    # 判斷 '-' 是否在數字之間，若是則替換為 '~'
    answer = re.sub(r'(?<=\d)-(?=\d)', '~', answer)  # 將數字之間的 '-' 替換為 '~'

    # 將文字行最前面的 '-' 替換為 '●'，表示項目符號
    answer = re.sub(r'(?m)^-\s*', '● ', answer)  # 使用多行模式，匹配行首的 '-'

    # 替換其他標點符號
    answer = answer.replace('。', '。<br>').replace('：', '：<br>')

    return answer


# @user_login_required
def wisdomQA(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'wisdomQA.html')
