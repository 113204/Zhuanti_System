import logging

import bcrypt
import requests
import re

from django.contrib import messages
from django.shortcuts import render, redirect
from core.settings import API_URL as root
from utils.decorators import user_login_required
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotAllowed




# @user_login_required
def Udetail(request):
    if request.method == 'GET':
        email = request.session['email']
        r = requests.get(
            f'{root}user/detail/',
            params={'email': email},
            cookies={'sessionid': request.session['sessionid']}
        )
        result = r.json()
        user = result['data']
        return render(request, 'users-profile.html', {'user': user})

    elif request.method == 'POST':
        name = request.POST.get('name', '')
        gender = request.POST.get('gender', '')
        live = request.POST.get('live', '')
        phone = request.POST.get('phone', '')
        about = request.POST.get('about', '')

        # Validate phone number format
        phone_pattern = r'^\d{4}-\d{3}-\d{3}$'
        if not re.match(phone_pattern, phone):
            messages.error(request, '電話格式填寫錯誤，請重新修改')
            user = {
                'name': name,
                'gender': gender,
                'live': live,
                'phone': phone,
                'about': about
            }
            return render(request, 'users-profile.html', {'user': user, 'edit_tab_active': True})

        # Validate gender is not empty
        if gender == "":
            messages.error(request, '請選擇性別')
            user = {
                'name': name,
                'gender': gender,
                'live': live,
                'phone': phone,
                'about': about
            }
            return render(request, 'users-profile.html', {'user': user, 'edit_tab_active': True})

        data = {
            'email': request.session['email'],
            'name': name,
            'gender': gender,
            'live': live,
            'phone': phone,
            'about': about
        }

        try:
            r = requests.post(
                f'{root}user/detail/edit/',
                data=data,
                cookies={'sessionid': request.session['sessionid']}
            )
            result = r.json()

            if result['success'] is True:
                ret = redirect('/profile/')
                messages.success(request, '已修改資料成功')
                return ret
            else:
                messages.error(request, result.get('message', '資料修改失敗'))
                return redirect('/profile/')

        except requests.exceptions.RequestException as e:
            messages.error(request, '伺服器錯誤，請稍後再試')
            return redirect('/profile/')

    else:
        return HttpResponseNotAllowed(['GET', 'POST'])

logger = logging.getLogger(__name__)

# 變更密碼
@user_login_required
def change_password(request):
    if request.method == 'GET':
        email = request.session['email']
        r = requests.get(
            f'{root}user/detail/',
            params={'email': email},
            # 'user_id': request.COOKIES['user_id'],
            cookies={'sessionid': request.session['sessionid']}
        )
        result = r.json()
        user = result['data']
        return render(request, 'users-password.html', {'user': user})

    # oldpass = request.POST['oldpass']
    newpass = request.POST['newpass']
    re_newpass = request.POST['re_newpass']
    email = request.session['email']
    # 更新密码
    hashed_password = bcrypt.hashpw(newpass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


    # 验证旧密码是否正确
    # if not bcrypt.checkpw(oldpass.encode('utf-8'), request.user.password.encode('utf-8')):
    #     messages.error(request, '舊密碼不正確')
    #     return redirect('/changepass/')

    # 验证新密码是否符合要求
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}$', newpass):
        messages.error(request, '密碼格式錯誤，必須包含大小寫字母、數字和特殊字符，且至少8個字符')
        return redirect('/changepass/')

    # 验证新密码与确认密码是否匹配
    if newpass != re_newpass:
        messages.error(request, '新密碼與確認密碼不一致')
        return redirect('/changepass/')

    data = {
        'email': email,
        'password': hashed_password,
    }

    r = requests.post(
        f'{root}user/pass/edit/',
        data=data,
        cookies={'sessionid': request.session['sessionid']}
    )

    result = r.json()

    if result['success'] is True:
        ret = redirect('/profile/')
        messages.success(request, '密碼變更成功')
        return ret
    else:
        messages.error(request, '密碼格式填寫錯誤，請重新修改')
        return redirect('/changepass/')