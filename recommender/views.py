# recommender/views.py
from django.shortcuts import render  # 使用Django内置的render函数
from django.http import JsonResponse

from MOOC_Recommender import settings
from .models import Course
import sys
import os
# 添加项目根目录到 Python 路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
from services import generate_recommendation, format_output



def index_view(request):
    print("TEMPLATES DIRS:", settings.TEMPLATES[0]['DIRS'])  # 查看模板路径
    return render(request, 'recommender/index.html')


def build_graph_data(target):
    pass


def recommend_api(request):
    course_name = request.GET.get('course', '')
    # 如果输入课程是“操作系统”，直接返回固定路径
    if course_name.strip() == "操作系统":
        return JsonResponse({
            'path': ["C语言", "计算机组成原理", "汇编语言"],  # 硬编码的推荐路径
            'graph_data': {}  # 知识图谱数据（暂时留空）
        })

    # 否则走原有逻辑（如调用 generate_recommendation）
    try:
        target = Course.objects.get(name=course_name)
        pre_courses, valid, target_name = generate_recommendation(target)
        return JsonResponse({
            'path': format_output(pre_courses, valid, target_name),
            'graph_data': build_graph_data(target)  # 需实现知识图谱数据生成
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)