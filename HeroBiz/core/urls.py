from django.contrib import admin
from django.urls import path
from views import views, auth_views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('test/', views.test),
    #主頁
    path('', views.index),
    #登入、登出、註冊
    path('login/', auth_views.login),
    path('logout/', auth_views.logout),
    path('register/', views.register),

    path('profile/', views.profile),
    path('appointment/', views.appointment),
    path('record/', views.record),
    path('development/', views.development),
    path('detect/', views.detect),
    path('wisdomQA/', views.wisdomQA),
]
