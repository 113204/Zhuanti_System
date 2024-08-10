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

