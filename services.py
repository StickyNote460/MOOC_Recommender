# services.py（根目录）
import os
import django
import sys
import re
import networkx as nx
from django.db.models import Q, Count
from django.core.exceptions import ObjectDoesNotExist

# 初始化 Django 环境
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MOOC_Recommender.settings')
django.setup()

from recommender.models import Course, Concept, PrerequisiteDependency, CourseConcept


# services.py（异常类）
class RecommendationError(Exception):
    """推荐系统基础异常"""


class CourseNotFoundError(RecommendationError):
    """课程不存在异常"""

    def __init__(self, course_name):
        self.course_name = course_name
        super().__init__(f"课程 '{course_name}' 不存在")


class InvalidInputError(RecommendationError):
    """无效输入异常"""

# --------------------------
# 文本解析模块
# --------------------------

def extract_course_names(text):
    """从复杂文本中提取有效课程名称"""
    text = re.sub(r'[\n\r\t\u3000]+', ' ', text)
    text = re.sub(r'[^\w\u4e00-\u9fa5、，,\.]', ' ', text)
    pattern = r'([\u4e00-\u9fa5]{2,}(?:[\s\-·\.][\u4e00-\u9fa5]+)*)'
    matches = re.findall(pattern, text)
    stop_words = {'无', '基础', '知识', '能力', '相关', '课程', '要求'}
    return [name.strip('、，, ')
            for name in matches
            if len(name) > 1 and name not in stop_words]


# --------------------------
# 课程匹配模块
# --------------------------

def match_courses(names):
    """分优先级匹配课程（精确→模糊）"""
    matched = set()

    # 第一轮：精确匹配
    exact_matches = Course.objects.filter(name__in=names)
    matched.update(exact_matches)
    remaining = set(names) - set(m.name for m in exact_matches)

    # 第二轮：模糊匹配（名称包含）
    for name in remaining:
        clean_name = re.sub(r'(基础|导论|高级|实践)$', '', name)
        qs = Course.objects.filter(name__icontains=clean_name)
        if qs.exists():
            matched.add(qs.first())

    return list(matched)


# --------------------------
# 概念覆盖计算模块
# --------------------------

def get_concept_coverage(target_course):
    """计算概念覆盖信息"""
    # 构建概念依赖图
    G = nx.DiGraph()
    concepts = {c.id: c for c in Concept.objects.all()}
    for c in concepts.values():
        G.add_node(c.id)
    for dep in PrerequisiteDependency.objects.all():
        G.add_edge(dep.prerequisite.id, dep.target.id)

    # 获取所有必需前驱概念
    target_concepts = set(target_course.concepts.values_list('id', flat=True))
    required = set()
    for cid in target_concepts:
        required.update(nx.ancestors(G, cid))
    required = required - target_concepts  # 排除自身

    if not required:
        return None, None  # 无前驱概念

    # 获取覆盖这些概念的课程
    candidates = Course.objects.exclude(id=target_course.id).annotate(
        coverage=Count('concepts', filter=Q(concepts__id__in=required))
    )

    # 计算覆盖度
    total = len(required)
    valid_candidates = []
    for course in candidates:
        coverage_rate = course.coverage / total if total > 0 else 0
        if coverage_rate > 0.6:
            valid_candidates.append((coverage_rate, course))

    return required, valid_candidates


# --------------------------
# 核心推荐逻辑（修复返回值数量问题）
# --------------------------

def generate_recommendation(target_course):
    """生成推荐路径（返回三元组）"""
    """主推荐逻辑（需传入有效的 Course 对象）"""
    if not isinstance(target_course, Course):
        raise InvalidInputError("target_course 必须是 Course 对象")

    try:
        # 第一阶段：解析prerequisites字段
        if target_course.prerequisites:
            names = extract_course_names(target_course.prerequisites)
            if names:
                matched = match_courses(names)
                if matched:
                    return matched, True, target_course.name

        # 第二阶段：基于概念覆盖推荐
        required, candidates = get_concept_coverage(target_course)

        if not required:
            return ["本课程为基础课，无前继课程"], False, target_course.name

        if not candidates:
            return ["无满足覆盖要求的前继课程。本课程为基础课"], False, target_course.name

        # 按覆盖率和课程质量排序
        candidates.sort(reverse=True, key=lambda x: (x[0], -x[1].difficulty))
        top3 = [c[1] for c in candidates[:3]]

        return top3, True, target_course.name
    except Exception as e:
        raise RecommendationError(f"推荐失败: {str(e)}") from e

# --------------------------
# 格式化输出（修复参数传递问题）
# --------------------------

def format_output(pre_courses, is_valid, target_name):
    """生成 {A，B，C}-->目标课程 格式"""
    if not is_valid:
        return f"{pre_courses[0]}"

    if len(pre_courses) == 0 or not isinstance(pre_courses[0], Course):
        return f"{{}}-->{target_name}"

    # 处理课程名称列表
    pre_names = [c.name for c in pre_courses]
    pre_str = "{" + "，".join(pre_names) + "}"
    return f"{pre_str}-->{target_name}"


if __name__ == "__main__":
    try:
        course_name = "操作系统（自主模式）"
        target = Course.objects.get(name=course_name)
        #不手动设置prerequisites字段的值
        pre_courses, valid, target_name = generate_recommendation(target)
        print("推荐路径:", format_output(pre_courses, valid, target_name))
    except ObjectDoesNotExist:
        print(f"错误：课程 {course_name} 不存在")
    except Exception as e:
        print(f"运行时错误: {str(e)}")

#
# # --------------------------
# # 执行入口（修复解包问题）
# # --------------------------
#
# if __name__ == "__main__":
#     try:
#         course_name = "操作系统（自主模式）"
#         target = Course.objects.get(name=course_name)
#         #不手动设置prerequisites字段的值
#         pre_courses, valid, target_name = generate_recommendation(target)
#         print("推荐路径:", format_output(pre_courses, valid, target_name))
#
#         # 测试案例 1：有效prerequisites字段
#         target.prerequisites = "数据结构、C语言"
#         pre_courses, valid, target_name = generate_recommendation(target)
#         print("推荐路径:", format_output(pre_courses, valid, target_name))
#
#         # 测试案例 2：基于概念覆盖
#         target.prerequisites = "无"
#         pre_courses, valid, target_name = generate_recommendation(target)
#         print("推荐路径:", format_output(pre_courses, valid, target_name))
#
#         # 测试案例 3：基础课程
#         target.prerequisites = ""
#         target.concepts.clear()  # 清空关联概念
#         pre_courses, valid, target_name = generate_recommendation(target)
#         print("推荐路径:", format_output(pre_courses, valid, target_name))
#
#     except ObjectDoesNotExist:
#         print(f"错误：课程 {course_name} 不存在")
#     except Exception as e:
#         print(f"运行时错误: {str(e)}")