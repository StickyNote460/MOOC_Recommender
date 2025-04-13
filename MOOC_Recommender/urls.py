"""
URL configuration for MOOC_Recommender project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
#MOOC_Recommender/urls.py
from django.contrib import admin
from django.urls import path
from recommender import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/recommender/', views.index_view, name='index'),#新增一个api
    path('api/recommend/', views.recommend_api, name='recommend_api'),
    # 新增根路径路由，直接渲染 index.html
    path('', views.index_view, name='root'),  # ✅ 添加这一行
]