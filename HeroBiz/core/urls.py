from django.contrib import admin
from django.urls import path
from views import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', views.index),
]
