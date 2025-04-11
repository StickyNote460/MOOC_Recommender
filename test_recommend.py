# test_recommend.py（根目录）
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MOOC_Recommender.settings')
django.setup()

from recommender.models import Course
from services import generate_prerequisite_path

def test(course_name):
    try:
        course = Course.objects.get(name=course_name)
        path = generate_prerequisite_path(course)
        print(f"路径: {' → '.join(path)}")
    except Course.DoesNotExist:
        print("课程不存在")

if __name__ == '__main__':
    test("自然灾害")