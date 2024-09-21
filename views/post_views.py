import logging
from datetime import datetime
import pytz

import bcrypt
import requests
import re

from django.contrib import messages
from django.db.models import Max
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

    # 设置台北时区
    taipei_tz = pytz.timezone('Asia/Taipei')
    for p in post:
        if 'date' in p:
            # 将 ISO 格式的日期时间字符串解析为 datetime 对象
            date = datetime.fromisoformat(p['date'].replace('Z', '+00:00'))
            # 转换为台北时区
            date = date.astimezone(taipei_tz)
            # 格式化为指定格式
            p['formatted_date'] = date.strftime('%Y-%m-%d %H:%M:%S')

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
        # 转换日期为台北时间
        taipei_tz = pytz.timezone('Asia/Taipei')
        for p in post:
            if 'date' in p:
                try:
                    date = datetime.fromisoformat(p['date'].replace('Z', '+00:00'))
                    date = date.astimezone(taipei_tz)
                    p['formatted_date'] = date.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError as e:
                    print(f"Error parsing date: {e}")
                    p['formatted_date'] = p['date']  # 如果解析失败，保留原始日期
    else:
        post = []

    # 处理消息数据
    if message_result.get('success'):
        message = message_result['data']
        # 转换评论日期为台北时间
        for msg in message:
            if 'date' in msg:
                try:
                    date = datetime.fromisoformat(msg['date'].replace('Z', '+00:00'))
                    date = date.astimezone(taipei_tz)
                    msg['formatted_date'] = date.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError as e:
                    print(f"Error parsing date: {e}")
                    msg['formatted_date'] = msg['date']  # 如果解析失败，保留原始日期
    else:
        message = []  # 确保 messages 是一个空列表

    # 将文章数据和 no 传递给模板
    return render(request, 'post_detail.html', {'post': post, 'message': message, 'no': no})

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

        # 获取当前日期和时间
        current_date = datetime.now().isoformat()  # 转换为 ISO 8601 字符串格式

        data = {
            'usermail': usermail_str,
            'title': title,
            'text': text,
            'date': current_date,  # 添加日期时间到数据中，已转换为字符串
        }

        try:
            response = requests.post(
                f'{root}post/addpost/',
                json=data,  # 使用 json 参数传递数据
                cookies={'sessionid': request.COOKIES.get('sessionid')}
            )
            response.raise_for_status()
            result = response.json()

            # if result.get('success', False):
            #     messages.success(request, '文章已成功新增')
            # else:
            #     messages.error(request, '新增文章失败')
        except requests.RequestException as e:
            messages.error(request, f'请求失败: {str(e)}')
        except ValueError as e:
            messages.error(request, f'解析响应失败: {str(e)}')

        return redirect('/post')

    return render(request, 'addpost.html')


# 新增留言
@user_login_required
def AddMessage(request):
    if request.method == 'GET':
        no = request.GET.get('no')  # 从 URL 中获取帖子编号
        email = request.COOKIES.get('email')
        if not email:
            messages.error(request, '未找到用户信息')
            return redirect('/login')

        # 获取用户信息
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

        # 获取文章内容并传递给模板
        post_url = f'{root}post/post/detail/{no}/'
        try:
            post_response = requests.get(
                post_url,
                cookies={'sessionid': request.COOKIES.get('sessionid')}
            )
            post_response.raise_for_status()
            post_result = post_response.json()
            post = post_result.get('data', {})
        except requests.RequestException as e:
            messages.error(request, f'获取文章信息失败: {str(e)}')
            post = {}
        except ValueError as e:
            messages.error(request, f'解析响应失败: {str(e)}')
            post = {}

        # 提取 nopost 的值，确保它不是 None
        nopost = post.get('no', no)
        if not nopost:
            messages.error(request, '帖子编号无效')
            return redirect('/')

        return render(request, 'addmessage.html', {'user': user, 'no': no, 'post': post, 'nopost': nopost})

    if request.method == 'POST':
        nopost = request.POST.get('nopost')  # 获取关联的帖子编号
        text = request.POST.get('text')  # 获取评论内容
        usermail_str = request.COOKIES.get('email')

        if not nopost:
            messages.error(request, '帖子编号无效')
            return redirect('/')

        # 获取当前日期和时间，转换为 ISO 8601 字符串格式
        taipei_tz = pytz.timezone('Asia/Taipei')
        current_date = datetime.now(taipei_tz).isoformat()

        data = {
            'nopost': nopost,
            'usermail': usermail_str,
            'text': text,
            'date': current_date,  # 添加日期时间到数据中，已转换为字符串
        }

        try:
            response = requests.post(
                f'{root}post/addmessage/',
                json=data,  # 使用 json 参数传递数据
                cookies={'sessionid': request.COOKIES.get('sessionid')}
            )
            response.raise_for_status()
            result = response.json()

            # if result.get('success', False):
            #     messages.success(request, '评论已成功新增')
            # else:
            #     messages.error(request, '新增评论失败')
        except requests.RequestException as e:
            messages.error(request, f'请求失败: {str(e)}')
        except ValueError as e:
            messages.error(request, f'解析响应失败: {str(e)}')

        # 从 POST 数据中获取 nopost 的值，并重定向到帖子详情页
        return redirect(f'/post/detail/{nopost}/')

    return render(request, 'addmessage.html')

# 編輯貼文
@user_login_required
def EditPost(request, no):
    if not no:
        return HttpResponseBadRequest("Missing 'no' parameter")

    post_url = f'{root}post/post/detail/{no}/'

    if request.method == 'GET':
        try:
            # 获取文章数据
            post_response = requests.get(
                post_url,
                cookies={'sessionid': request.COOKIES.get('sessionid')}
            )
            post_response.raise_for_status()
            post_result = post_response.json()

        except requests.RequestException as e:
            print(f'RequestException: {e}')
            return HttpResponseServerError("Request failed")
        except ValueError as e:
            print(f'JSONDecodeError: {e}')
            return HttpResponseServerError("Failed to decode JSON response")

        # 处理文章数据
        if post_result.get('success'):
            post = post_result['data']
            # 转换日期为台北时间（如果需要）
            taipei_tz = pytz.timezone('Asia/Taipei')
            if 'date' in post:
                try:
                    date = datetime.fromisoformat(post['date'].replace('Z', '+00:00'))
                    date = date.astimezone(taipei_tz)
                    post['formatted_date'] = date.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError as e:
                    print(f"Error parsing date: {e}")
                    post['formatted_date'] = post['date']  # 如果解析失败，保留原始日期
        else:
            post = {}

        # 只渲染编辑表单的模板，不需要消息数据
        return render(request, 'editpost.html', {'post': post, 'no': no})

    elif request.method == 'POST':
        title = request.POST.get('title')
        text = request.POST.get('text')
        usermail_str = request.COOKIES.get('email')

        if not title or not text:
            messages.error(request, '标题或内容不能为空')
            return redirect(f'/post/editpost/{no}/')

        # 获取当前日期和时间，转换为 ISO 8601 字符串格式
        taipei_tz = pytz.timezone('Asia/Taipei')
        current_date = datetime.now(taipei_tz).isoformat()

        data = {
            'no': no,
            'usermail': usermail_str,
            'title': title,
            'text': text,
            'date': current_date,  # 添加日期时间到数据中，已转换为字符串
        }

        try:
            response = requests.post(
                f'{root}post/editpost/',  # 修改为编辑帖子 URL
                json=data,  # 使用 json 参数传递数据
                cookies={'sessionid': request.COOKIES.get('sessionid')}
            )
            response.raise_for_status()
            result = response.json()

            if result.get('success', False):
                messages.success(request, '文章已成功编辑')
            else:
                messages.error(request, '编辑文章失败')
        except requests.RequestException as e:
            messages.error(request, f'请求失败: {str(e)}')
        except ValueError as e:
            messages.error(request, f'解析响应失败: {str(e)}')

        # 返回到帖子详情页
        return redirect(f'/post/detail/{no}/')

# 刪除貼文
@user_login_required
def DeletePost(request, no):
    if not no:
        return HttpResponseBadRequest("缺少 'no' 参数")

    delete_url = f'{root}post/deletepost/{no}/'

    try:
        # 执行删除请求
        response = requests.post(
            delete_url,  # 使用 POST 请求
            cookies={'sessionid': request.COOKIES.get('sessionid')}
        )
        response.raise_for_status()
        result = response.json()

        if result.get('success', False):
            messages.success(request, '文章已成功删除')
        else:
            messages.error(request, '删除文章失败')
    except requests.RequestException as e:
        messages.error(request, f'请求失败: {str(e)}')
    except ValueError as e:
        messages.error(request, f'解析响应失败: {str(e)}')

    # 返回到帖子列表页
    return redirect('/profile')