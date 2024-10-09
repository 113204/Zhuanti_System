from json import JSONDecodeError

import requests
import re
import bcrypt

from django.http import HttpResponse
from django.shortcuts import render, redirect
from core.settings import API_URL as root
from django.contrib import messages

root += 'auth'


# 登入
def login(request):
    # return render(request, 'login.html')

    # 設置若已經登入過，所導向的畫面
    if 'email' in request.COOKIES:
        messages.success(request, '已成功登入')
        return redirect('/')

    if request.method == 'GET':
        return render(request, 'pages-login.html')

    email = request.POST['your_name']
    password = request.POST['your_pass']

    data = {
        'email': email,
        'password': password
    }

    r = requests.post(
        f'{root}/login/',
        data=data
    )

    result = r.json()

    if result['success'] is True:
        ret = redirect('/')
        ret.set_cookie('sessionid', result['sessionid'])
        ret.set_cookie('email', email)
        request.session['email'] = email
        request.session.save()
        messages.success(request, '已成功登入')

        # 打印存储在 COOKIES 中的电子邮件地址
        print("Email stored in cookies:", request.COOKIES.get('email'))
        return ret
    else:
        messages.error(request, '帳號或密碼錯誤')
        return redirect('/login')


# 登出
def logout(request):
    # 删除本地会话中的 email 键
    if 'email' in request.session:
        del request.session['email']
        request.session.modified = True  # 标记会话已修改

    # 删除本地的 cookies
    ret = redirect('/')
    ret.delete_cookie('sessionid')
    ret.delete_cookie('email')

    # 向服务器发送登出请求
    requests.post(
        f'{root}/logout/',
        cookies={'sessionid': request.COOKIES['sessionid']}
    )

    messages.success(request, '已成功登出')
    return ret


# 註冊
def register(request):
    if request.method == 'GET':
        return render(request, 'pages-register.html')

    email = request.POST['email']
    name = request.POST['name']
    password = request.POST['pass']
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')  # 使用 bcrypt 加密密码
    gender = request.POST.get('gender', None)
    # live = request.POST['live']
    phone = request.POST['phone']
    re_pass = request.POST['re_pass']

    # 驗證電子郵件格式
    if not re.match(r'^[\w\.-]+@[\w\.-]+(\.[\w]+)+$', email):
        messages.error(request, '電子郵件格式錯誤')
        return redirect('/register')

    # 驗證密碼格式是否符合要求]
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}$', password):
        messages.error(request, '密碼格式錯誤，必須包含大小寫字母、數字和特殊字符，且至少8個字符')
        return redirect('/register')

    # 驗證密碼和重複密碼是否匹配
    if password != re_pass:
        messages.error(request, '密碼與重複密碼不一致')
        return redirect('/register')

    # 驗證電話號碼格式
    if not re.match(r'^\d{4}-\d{3}-\d{3}$', phone):
        messages.error(request, '電話號碼格式錯誤，請輸入格式為 XXXX-XXX-XXX 的號碼')
        return redirect('/register')

    # 驗證性別是否選擇
    if not gender:
        messages.error(request, '請選擇性別')
        return redirect('/register')

    data = {
        'email': email,
        'name': name,
        'password': hashed_password,  # 使用加密后的密码
        'gender': gender,
        # 'live': live,
        'phone': phone,
        'permission': 0,
    }

    r = requests.post(
        f'{root}/register/',
        data=data,
    )

    result = r.json()

    if result['success'] is True:
        ret = redirect('/login')
        messages.success(request, '已註冊成功')
        return ret
    else:
        messages.error(request, '信箱已被註冊或是註冊時欄位格式填寫錯誤，請重新註冊')
        return redirect('/register')


# 忘記密碼頁面視圖
def ForgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if email:
            response = requests.post(
                f'{root}/forget/',  # 後端 API 端點的 URL
                json={'email': email}
            )

            if response.status_code == 200:
                # 郵件成功發送，設置消息並重定向到登入頁面
                messages.success(request, '請查看您的電子郵件以重設密碼。')
                return redirect('login')  # 確保在 urls.py 中將 'login' 定義為登入頁的 URL 名稱
            else:
                messages.error(request, '發送郵件失敗，請檢查電子郵件地址是否正確。')
                return render(request, 'forget-pass.html')

    return render(request, 'forget-pass.html')


# 密碼重設頁面視圖
def PasswordReset(request, uidb64, token):
    if request.method == 'POST':
        new_password = request.POST.get('password')
        re_pass = request.POST.get('re_pass')

        # 確保新密碼存在
        if not new_password or not re_pass:
            messages.error(request, '請輸入新密碼及重複密碼。')
            return render(request, 'reset-pass.html', {'uid': uidb64, 'token': token})

        # 驗證密碼格式
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}$', new_password):
            messages.error(request, '密碼格式錯誤，必須包含大小寫字母、數字和特殊字符，且至少8個字符。')
            return render(request, 'reset-pass.html', {'uid': uidb64, 'token': token})

        # 驗證新密碼和重複密碼是否一致
        if new_password != re_pass:
            messages.error(request, '新密碼與重複密碼不一致。')
            return render(request, 'reset-pass.html', {'uid': uidb64, 'token': token})

        # 加密新密碼
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # 發送 POST 請求到後端的重設密碼 API 端點
        response = requests.post(
            f'{root}/reset-password/',  # 後端 API 端點的 URL
            json={'uid': uidb64, 'token': token, 'password': hashed_password}  # 使用加密后的密碼
        )

        # 獲取 API 回應
        if response.status_code == 200:
            # 密碼重設成功，重定向到登入頁面
            messages.success(request, '密碼重設成功，請登入。')
            return redirect('/login/')  # 替換成您的登入頁面 URL
        else:
            # 如果後端返回錯誤，根據返回的錯誤信息調整
            error_message = response.json().get('error', '密碼重設失敗，請確認您的連結是否有效。')
            messages.error(request, error_message)
            return render(request, 'reset-pass.html', {'uid': uidb64, 'token': token})

    # 如果是 GET 請求，則顯示重設密碼頁面
    context = {'uid': uidb64, 'token': token}
    return render(request, 'reset-pass.html', context)


