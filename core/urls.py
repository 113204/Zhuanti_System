from django.contrib import admin
from django.urls import path
from views import views, auth_views, user_views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('test/', views.test),
    #主頁
    path('', views.index),
    #登入、登出、註冊
    path('login/', auth_views.login),
    path('logout/', auth_views.logout),
    path('register/', auth_views.register),
    #使用者資料
    path('profile/', user_views.Udetail),
    path('changepass/', user_views.change_password, name='change_password'),
    # path('editusers/', user_views.EditUserDetail),

    # 忘記密碼
    path('forgetpass/', auth_views.forget_password),

    path('appointment/', views.appointment),
    path('record/', views.record),
    path('development/', views.development),
    path('detect/', views.detect),
    path('wisdomQA/', views.wisdomQA),
]
