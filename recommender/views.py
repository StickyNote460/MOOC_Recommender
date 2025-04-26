# recommender/views.py
from django.shortcuts import render  # 使用Django内置的render函数
from django.http import JsonResponse
import json
from django.db.models import Q

from MOOC_Recommender import settings
from .models import Course, PrerequisiteDependency
import sys
import os
# 添加项目根目录到 Python 路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
from services import generate_recommendation, format_output



def index_view(request):
    print("TEMPLATES DIRS:", settings.TEMPLATES[0]['DIRS'])  # 查看模板路径
    return render(request, 'recommender/index.html')



def build_graph_data(target_course):
    # 获取目标课程关联的所有概念
    target_concepts = set(target_course.concepts.all())

    # 获取所有相关的前置依赖关系
    dependencies = PrerequisiteDependency.objects.filter(
        Q(target__in=target_concepts) |
        Q(prerequisite__in=target_concepts)
    ).select_related('prerequisite', 'target')

    # 收集所有相关概念
    all_concepts = set()
    for dep in dependencies:
        all_concepts.add(dep.prerequisite)
        all_concepts.add(dep.target)

    # 构建节点数据
    nodes = [
        {
            'id': str(concept.id),
            'name': concept.name,
            'is_target': concept in target_concepts
        }
        for concept in all_concepts
    ]

    # 构建边数据
    links = [
        {
            'source': str(dep.prerequisite.id),
            'target': str(dep.target.id)
        }
        for dep in dependencies
    ]

    return {'nodes': nodes, 'links': links}


def recommend_api(request):
    course_name = request.GET.get('course', '').strip()

    # #
    # if course_name == "操作系统":
    #     return JsonResponse({
    #         'pre_courses': ["C语言", "计算机组成原理", "汇编语言"],
    #         'target': "操作系统",
    #         'is_valid': True,
    #         'graph_data': {}
    #     }, json_dumps_params={'ensure_ascii': False})

    try:
        target = Course.objects.get(name=course_name)
        pre_courses, valid, _ = generate_recommendation(target)

        # 构造返回数据
        response_data = {
            'is_valid': valid,
            'target': target.name,
            'graph_data': build_graph_data(target)
        }

        if valid:
            # 有效推荐：返回前驱课程列表
            response_data['pre_courses'] = [c.name for c in pre_courses]
        else:
            # 无效推荐：直接返回错误信息
            response_data['error_msg'] = pre_courses[0]  # 取第一条错误信息

        return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})

    except Course.DoesNotExist:
        return JsonResponse({'error': '课程不存在'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)