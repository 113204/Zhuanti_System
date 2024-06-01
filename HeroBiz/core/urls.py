from django.contrib import admin
from django.urls import path
from views import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', views.test),
    path('', views.index),
    path('login/', views.login),
    path('register/', views.register),
    path('profile/', views.profile),
    path('appointment/', views.appointment),
    path('record/', views.record),
    path('development/', views.development),
    path('detect/', views.detect),
    path('wisdomQA/', views.wisdomQA),
]
