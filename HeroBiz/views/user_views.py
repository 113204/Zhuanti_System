import requests
from django.contrib import messages
from django.shortcuts import render, redirect
from core.settings import API_URL as root
from utils.decorators import user_login_required
from django.http import HttpResponseForbidden


@user_login_required
def Udetail(request):
    email = request.session['email']

    # 构造查询参数
    params = {'email': email}

    # 发送请求，并传递查询参数
    r = requests.get(
        f'{root}user/detail/',
        params=params,
        cookies={'sessionid': request.session['sessionid']}
    )
    result = r.json()
    user = result['data']
    return render(request, 'users-profile.html', {'user': user})