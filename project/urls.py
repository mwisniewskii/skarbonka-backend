"""project URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Django
from django.conf.urls import url
from django.contrib import admin
from django.urls import include
from django.urls import path

from accounts import views

userList = views.UserViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

userDetail = views.UserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('users/', userList, name='users'),
    path('users/<int:pk>/', userDetail, name='user'),

]
