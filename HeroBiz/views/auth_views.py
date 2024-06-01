import requests
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

    # html中輸入欄位，有id=xxx，把xxx填入至後面''中的文字內
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
        messages.success(request, '已成功登入')
        return ret
    else:
        messages.error(request, '帳號或密碼錯誤')
        return redirect('/login/')


# 登出
def logout(request):
    requests.post(
        f'{root}/logout/',
        cookies={'sessionid': request.COOKIES['sessionid']}
    )

    ret = redirect('/login/')
    ret.delete_cookie('sessionid')
    ret.delete_cookie('email')
    messages.success(request, '已成功登出')
    return ret