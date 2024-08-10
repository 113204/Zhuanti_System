from django.contrib import admin
from django.urls import path
from views import views, auth_views, user_views, post_views

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

    # 文章列表
    path('post/', post_views.Post),
    path('post/detail/<int:no>/', post_views.PostDetail, name='post_detail'),
    # 開發團隊
    path('development/', views.development),

    # 健身監測
    path('detect1/', views.detect1, name='detect1'),
    path('detect/', views.detect, name='detect'),
    
    # 教學影片
    path('video/', views.video),
    
    # 智慧問答
    path('wisdomQA/', views.wisdomQA),
]
