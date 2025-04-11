from django.shortcuts import render,HttpResponse

def index(request):
    return HttpResponse("hello world!")

# Create your views here.
# recommender/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
#from ..services import generate_prerequisite_path  # 从根目录导入
from services import generate_prerequisite_path  # 直接导入根目录下的 services.py
from .models import Course


@require_GET
def course_path(request):
    course_name = request.GET.get('course')
    if not course_name:
        return JsonResponse({'error': '参数缺失: course'}, status=400)

    try:
        course = Course.objects.get(name=course_name)
    except Course.DoesNotExist:
        return JsonResponse({'error': '课程不存在'}, status=404)

    path = generate_prerequisite_path(course)
    return JsonResponse({'course': course_name, 'path': ' → '.join(path)})