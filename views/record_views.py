from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from core.settings import API_URL as root
import requests

def addrecord(request):
    if request.method == 'POST':
        user_email = request.COOKIES.get('email')
        count = request.POST.get('count')
        left_errors = request.POST.get('left_errors')
        right_errors = request.POST.get('right_errors')
        sport_time = request.POST.get('sport_time')

        # 轉換日期時間格式
        current_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # ISO 8601 格式

        data = {
            'user_email': user_email,
            'count': count,
            'datetime': current_date,
            'left_errors': left_errors,
            'right_errors': right_errors,
            'sport_time': sport_time
        }

        try:
            response = requests.post(
                f'{root}record/record/',
                json=data,
                cookies={'sessionid': request.COOKIES.get('sessionid')}
            )
            response.raise_for_status()
            result = response.json()

            if result.get('message'):
                # 添加成功，返回 JSON 响应
                return JsonResponse({'message': '運動紀錄已新增成功', 'redirect_url': '/record'}, status=200)
            else:
                # 处理失败情况
                return JsonResponse({'error': '新增紀錄時發生錯誤，請重新嘗試'}, status=400)

        except requests.HTTPError as http_err:
            return JsonResponse({'error': f'HTTP 錯誤: {http_err}'}, status=400)
        except requests.RequestException as e:
            return JsonResponse({'error': f'無法連線到伺服器: {str(e)}'}, status=400)