# urls.py（根目录）
from django.urls import path

from recommender.views import course_path

urlpatterns = [
    path('api/path/', course_path, name='course-path'),
]