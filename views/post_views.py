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
    if not no:
        return HttpResponseBadRequest("Missing 'no' parameter")

    post_url = f'{root}post/post/detail/{no}/'
    post_message_url = f'{root}post/post/message/{no}/'  # 不需要额外传递 nopost

    try:
        # 获取文章数据
        post_response = requests.get(
            post_url,
            cookies={'sessionid': request.COOKIES.get('sessionid')}
        )
        post_response.raise_for_status()
        post_result = post_response.json()

        # 获取与文章相关的消息数据
        message_response = requests.get(
            post_message_url,
            cookies={'sessionid': request.COOKIES.get('sessionid')}
        )
        message_response.raise_for_status()
        message_result = message_response.json()

    except requests.RequestException as e:
        print(f'RequestException: {e}')
        return HttpResponseServerError("Request failed")
    except ValueError as e:
        print(f'JSONDecodeError: {e}')
        return HttpResponseServerError("Failed to decode JSON response")

    # 处理文章数据
    if post_result.get('success'):
        post = [post_result['data']]
    else:
        post = []

    # 处理消息数据
    if message_result.get('success'):
        messages = message_result['data']
    else:
        messages = []  # 确保 messages 是一个空列表

    return render(request, 'post_detail.html', {'post': post, 'messages': messages})