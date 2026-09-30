"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from .views import (
    home, about, hello, calculate_sum, health_check,
    api_users_view, users_page_view, swagger_ui_view, swagger_json_view
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('about', about),
    path('hello/', hello, name='hello'),
    path('hello/<str:name>/', hello, name='hello_name'),
    path('sum/<int:num1>/<int:num2>/', calculate_sum, name='sum'),
    path('sum/<int:num1>/<int:num2>', calculate_sum),
    path('api/healt/', health_check, name='health_check'),
    path('api/healt', health_check),
    path('api/health/', health_check, name='health_check_alt'),
    path('api/health', health_check),
    path('api/users/', api_users_view, name='api_users'),
    path('api/users', api_users_view),
    path('api/users/<int:user_id>/', api_users_view, name='api_user_detail'),
    path('api/users/<int:user_id>', api_users_view),
    path('api/swagger/', swagger_ui_view, name='swagger_ui'),
    path('api/swagger', swagger_ui_view),
    path('api/swagger.json', swagger_json_view, name='swagger_json'),
    path('users/', users_page_view, name='users_page'),
    path('users', users_page_view),
]

