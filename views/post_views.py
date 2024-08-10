import logging

import bcrypt
import requests
import re

from django.contrib import messages
from django.shortcuts import render, redirect
from requests import JSONDecodeError

from core.settings import API_URL as root
from utils.decorators import user_login_required
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponseServerError
from django.http import HttpResponseNotAllowed


# root += 'post'

# 文章列表
@user_login_required
def Post(request):
    r = requests.get(
        f'{root}post/post/',
        cookies={'sessionid': request.COOKIES['sessionid']}
    )
    result = r.json()
    post = result['data']
    return render(request, 'post.html', {'post': post})

# 文章內文
@user_login_required
def PostDetail(request, no):
    # no = request.GET.get('no')
    if not no:
        return HttpResponseBadRequest("Missing 'no' parameter")

    post_url = f'{root}post/post/detail/{no}/'
    try:
        r = requests.get(
            post_url,
            cookies={'sessionid': request.COOKIES.get('sessionid')}
        )
        r.raise_for_status()
        result = r.json()
    except requests.RequestException as e:
        print(f'RequestException: {e}')
        return HttpResponseServerError("Request failed")
    except ValueError as e:
        print(f'JSONDecodeError: {e}')
        return HttpResponseServerError("Failed to decode JSON response")

    if result.get('success'):
        post = [result['data']]  # 包装成列表以匹配模板
    else:
        post = []

    return render(request, 'post_detail.html', {'post': post})