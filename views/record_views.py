from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from core.settings import API_URL as root
import requests

# 新增運動紀錄
def addrecord(request, posedetect_instance):
    # 檢查使用者是否登入
    if 'email' not in request.session:
        messages.error(request, '使用者未登入')
        return redirect('/login')

    # 從 session 中取得已登入的使用者 email
    user_email = request.session['email']

    if request.method == 'POST':
        # 使用 get_counter 方法來取得 counter 的值
        current_counter = posedetect_instance.get_counter()  # 取得 counter 的值
        datetime_str = request.POST.get('datetime')
        left_errors = request.POST.get('left_errors', 0)
        right_errors = request.POST.get('right_errors', 0)
        sport_time = request.POST.get('sport_time')

        # 驗證必要欄位是否存在
        if not all([datetime_str, sport_time]):
            messages.error(request, '請填寫所有必填欄位')
            return redirect('/detect')  # 假設這是新增紀錄的表單頁面路由

        # 解析日期時間字串
        try:
            datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messages.error(request, '日期時間格式不正確，應為 "YYYY-MM-DD HH:MM:SS"')
            return redirect('/detect')

        # 將資料組合成字典
        data = {
            'user_email': user_email,
            'count': current_counter,  # 將 current_counter 作為 count 的值
            'datetime': datetime_obj.strftime("%Y-%m-%d %H:%M:%S"),  # 格式化日期
            'left_errors': left_errors,
            'right_errors': right_errors,
            'sport_time': sport_time
        }

        # 發送 POST 請求到 API 進行儲存
        try:
            r = requests.post(f'{root}record/addrecord/', data=data)
            result = r.json()

            if result.get('success') is True:
                messages.success(request, '運動紀錄已新增成功')
                return redirect('/records')  # 假設這是運動紀錄列表頁面路由
            else:
                messages.error(request, '新增紀錄時發生錯誤，請重新嘗試')
                return redirect('/detect')

        except requests.RequestException as e:
            messages.error(request, f'無法連線到伺服器: {str(e)}')
            return redirect('/detect')

    # 如果不是 POST 請求，重定向至新增紀錄頁面（可選）
    return redirect('/record')  # 假設這是新增紀錄的表單頁面路由
