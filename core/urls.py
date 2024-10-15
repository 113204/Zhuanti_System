from django.contrib import admin
from django.urls import path
from views import views, auth_views, user_views, post_views, record_views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('test/', views.test),
    #主頁
    path('', views.index),

    # 隱私權政策
    path('privacypolicies/', views.privacypolicies),

    #登入、登出、註冊
    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout),
    path('register/', auth_views.register),

    #使用者資料
    path('profile/', user_views.Udetail, name='profile'),
    path('changepass/', user_views.change_password, name='change_password'),
    # path('editusers/', user_views.EditUserDetail),

    # 忘記密碼
    path('forgot-password/', auth_views.ForgotPassword, name='forgot_password'),
    # 重設密碼，包含 uid 和 token 參數
    path('reset-password/<uidb64>/<token>/', auth_views.PasswordReset, name='reset_password'),

    # 運動紀錄
    path('record/', user_views.getrecord, name='getrecord'),

    # 文章列表
    path('post/', post_views.Post),
    path('post/detail/<int:no>/', post_views.PostDetail, name='post_detail'),
    path('addpost/', post_views.AddPost),
    path('addmessage/', post_views.AddMessage, name='addmessage'),
    path('editpost/<int:no>/', post_views.EditPost, name='editpost'),
    path('deletepost/<int:no>/', post_views.DeletePost, name='deletepost'),

    # 開發團隊
    path('development/', views.development),

    # 健身監測
    path('detect1/', views.detect1, name='detect1'),
    path('detect/', views.detect, name='detect'),
    path('stop_camera/', views.stop_camera, name='stop_camera'),
    path('addrecord/', record_views.addrecord, name='addrecord'),
    
    # 教學影片
    path('video/', views.video),
    
    # 智慧問答
    path('wisdomQA/', views.wisdomQA),
]
