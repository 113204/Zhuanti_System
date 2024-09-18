import logging

import bcrypt
import requests
import re

from django.contrib import messages
from django.shortcuts import render, redirect
from requests import JSONDecodeError

from core.settings import API_URL as root
from utils.decorators import user_login_required
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotAllowed


@user_login_required
def Udetail(request):
    if request.method == 'GET':
        email = request.COOKIES['email']

        # 获取用户详细信息
        try:
            r_user = requests.get(
                f'{root}user/detail/',
                params={'email': email},
                cookies={'sessionid': request.COOKIES['sessionid']}
            )
            result_user = r_user.json()
            user = result_user['data']
        except requests.exceptions.RequestException as e:
            logger.error(f"获取用户详细信息失败: {e}")
            user = {}  # 如果获取用户信息失败，使用空字典

        # 获取用户发布的文章
        try:
            r_post = requests.get(
                f'{root}post/user/posts/',  # 使用 get_user_post 的 URL
                params={'email': email},
                cookies={'sessionid': request.COOKIES['sessionid']}
            )
            result_post = r_post.json()
            post = result_post['data']
        except requests.exceptions.RequestException as e:
            logger.error(f"获取用户文章失败: {e}")
            post = []  # 如果获取文章失败，使用空列表

        return render(request, 'users-profile.html', {'user': user, 'post': post})

    elif request.method == 'POST':
        name = request.POST.get('name', '')
        gender = request.POST.get('gender', '')
        # live = request.POST.get('live', '')
        phone = request.POST.get('phone', '')
        about = request.POST.get('about', '')

        # Validate phone number format
        phone_pattern = r'^\d{4}-\d{3}-\d{3}$'
        if not re.match(phone_pattern, phone):
            messages.error(request, '電話格式填寫錯誤，請重新修改')
            user = {
                'name': name,
                'gender': gender,
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
                'phone': phone,
                'about': about
            }
            return render(request, 'users-profile.html', {'user': user, 'edit_tab_active': True})

        data = {
            'email': request.COOKIES['email'],
            'name': name,
            'gender': gender,
            'phone': phone,
            'about': about
        }

        try:
            r = requests.post(
                f'{root}user/detail/edit/',
                data=data,
                cookies={'sessionid': request.COOKIES['sessionid']}
            )
            result = r.json()

            if result['success'] is True:
                ret = redirect('/profile')
                messages.success(request, '已修改資料成功')
                return ret
            else:
                messages.error(request, result.get('message', '資料修改失敗'))
                return redirect('/profile')

        except requests.exceptions.RequestException as e:
            messages.error(request, '伺服器錯誤，請稍後再試')
            return redirect('/profile')

    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


logger = logging.getLogger(__name__)


# 變更密碼
@user_login_required
def change_password(request):
    if request.method == 'GET':
        email = request.COOKIES['email']
        r = requests.get(
            f'{root}user/detail/',
            params={'email': email},
            # 'user_id': request.COOKIES['user_id'],
            cookies={'sessionid': request.COOKIES['sessionid']}
        )
        result = r.json()
        user = result['data']
        return render(request, 'users-password.html', {'user': user})

    if request.method == 'POST':
        newpass = request.POST['newpass']
        re_newpass = request.POST['re_newpass']
        email = request.POST.get('email')


        # 驗證新密碼是否符合要求
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}$', newpass):
            messages.error(request, '密碼格式錯誤，必須包含大小寫字母、數字和特殊字符，且至少8個字符')
            return redirect('/changepass')

        # 驗證新密碼與確認密碼是否匹配
        if newpass != re_newpass:
            messages.error(request, '新密碼與確認密碼不一致')
            return redirect('/changepass')

        if request.POST['newpass'] == request.POST['re_newpass']:
            # 更新密码
            hashed_password = bcrypt.hashpw(newpass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            data = {
                'email': request.COOKIES['email'],
                'password': hashed_password,
            }

            r = requests.post(
                f'{root}user/pass/edit/',
                data=data,
                cookies={'sessionid': request.COOKIES['sessionid']}
            )
            result = r.json()

            if result['success'] is True:
                ret = redirect('/profile')
                messages.success(request, '密碼變更成功')
                return ret
            else:
                messages.error(request, '密碼格式填寫錯誤，請重新修改')
                return redirect('/changepass')

