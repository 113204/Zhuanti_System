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

# 新增文章
@user_login_required
def AddPost(request):
    if request.method == 'GET':
        email = request.COOKIES.get('email')
        if not email:
            messages.error(request, '未找到用户信息')
            return redirect('/login')

        try:
            response = requests.get(
                f'{root}user/detail/',
                params={'email': email},
                cookies={'sessionid': request.COOKIES.get('sessionid')}
            )
            response.raise_for_status()
            result = response.json()
            user = result.get('data', {})
        except requests.RequestException as e:
            messages.error(request, f'获取用户信息失败: {str(e)}')
            user = {}
        except ValueError as e:
            messages.error(request, f'解析响应失败: {str(e)}')
            user = {}

        return render(request, 'addpost.html', {'user': user})

    if request.method == 'POST':
        title = request.POST.get('title')
        text = request.POST.get('text')
        usermail_str = request.COOKIES.get('email')

        # 确保从 POST 请求中获取的数据
        no_str = request.POST.get('no')
        if no_str is not None:
            try:
                no = int(no_str)  # 转换为整数
            except ValueError:
                no = None
        else:
            no = None

        # 生成下一个流水号（如果 no 不存在）
        if no is None:
            try:
                max_no = Post.objects.order_by('-no').first()
                next_no = max_no.no + 1 if max_no else 1
            except Exception as e:
                print(f'Error getting max_no: {e}')
                next_no = 1
        else:
            next_no = no

        data = {
            'no': next_no,
            'usermail': usermail_str,
            'title': title,
            'text': text,
        }

        try:
            response = requests.post(
                f'{root}post/addpost/',
                json=data,  # 使用 json 参数传递数据
                cookies={'sessionid': request.COOKIES.get('sessionid')}
            )
            response.raise_for_status()
            result = response.json()

            if result.get('success', False):
                messages.success(request, '文章已成功新增')
            else:
                messages.error(request, '新增文章失败')
        except requests.RequestException as e:
            messages.error(request, f'请求失败: {str(e)}')
        except ValueError as e:
            messages.error(request, f'解析响应失败: {str(e)}')

        return redirect('/post')

    return render(request, 'addpost.html')
