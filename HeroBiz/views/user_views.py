import requests
import re

from django.contrib import messages
from django.shortcuts import render, redirect
from core.settings import API_URL as root
from utils.decorators import user_login_required
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotAllowed



# @user_login_required
# def Udetail(request):
#     email = request.session['email']
#
#     # 构造查询参数
#     params = {'email': email}
#
#     # 发送请求，并传递查询参数
#     r = requests.get(
#         f'{root}user/detail/',
#         params=params,
#         cookies={'sessionid': request.session['sessionid']}
#     )
#     result = r.json()
#     user = result['data']
#     return render(request, 'users-profile.html', {'user': user})
#
# # 編輯個人資料(修改版)
# @user_login_required
# def EditUserDetail(request):
#     if request.method == 'GET':
#         email = request.COOKIES['email']
#         r = requests.get(
#             f'{root}user/detail/',
#             params={'email': email},
#             # 'user_id': request.COOKIES['user_id'],
#             cookies={'sessionid': request.COOKIES['sessionid']}
#         )
#         result = r.json()
#         user = result['data']
#         return render(request, 'users-profile.html', {'user': user})
#
#     name = request.POST['name']
#     gender = request.POST['gender']
#     live = request.POST['live']
#     phone = request.POST['phone']
#     about = request.POST['about']
#
#
#     data = {
#         'email': request.COOKIES['email'],
#         'name': name,
#         'gender': gender,
#         'live': live,
#         'phone': phone,
#         'about': about
#     }
#     # user_id = request.COOKIES['user_id']
#     r = requests.post(
#         f'{root}user/detail/edit/',
#         # params={'user_id': user_id},
#         data=data,
#         cookies={'sessionid': request.COOKIES['sessionid']}
#     )
#     result = r.json()
#
#
#     if result['success'] is True:
#         ret = redirect('/profile')
#         messages.success(request, '已修改資料成功')
#         return ret
#     else:
#         messages.error(request, '電話格式填寫錯誤，請重新修改')
#         return redirect('#')

@user_login_required
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
                ret = redirect('/profile')
                messages.success(request, '已修改資料成功')
                return ret
            else:
                messages.error(request, result.get('message', '資料修改失敗'))
                return redirect('#')

        except requests.exceptions.RequestException as e:
            messages.error(request, '伺服器錯誤，請稍後再試')
            return redirect('#')

    else:
        return HttpResponseNotAllowed(['GET', 'POST'])