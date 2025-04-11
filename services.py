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


# --------------------------
# 文本解析模块
# --------------------------

def extract_course_names(text):
    """从复杂文本中提取有效课程名称"""
    # 清洗文本并分段
    text = re.sub(r'[\n\r\t\u3000]+', ' ', text)
    text = re.sub(r'[^\w\u4e00-\u9fa5、，,\.]', ' ', text)

    # 匹配课程名称模式（至少2个中文字符开头）
    pattern = r'([\u4e00-\u9fa5]{2,}(?:[\s\-·\.][\u4e00-\u9fa5]+)*)'
    matches = re.findall(pattern, text)

    # 过滤无效词
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
        coverage=Count('concepts', filter=Q(concepts__id__in=required)))

    # 计算覆盖度
    total = len(required)
    valid_candidates = []
    for course in candidates:
        coverage_rate = course.coverage / total if total > 0 else 0
    if coverage_rate > 0.6:
        valid_candidates.append((coverage_rate, course))

    return required, valid_candidates


# --------------------------
# 核心推荐逻辑
# --------------------------

def generate_recommendation(target_course):
    """生成推荐路径"""
    # 第一阶段：解析prerequisites字段
    if target_course.prerequisites:
        # 提取课程名称并匹配
        names = extract_course_names(target_course.prerequisites)
        if names:
            matched = match_courses(names)
            if matched:
                return [c.name for c in matched], True

    # 第二阶段：基于概念覆盖推荐
    required, candidates = get_concept_coverage(target_course)

    if not required:
        return ["本课程为基础课，无前继课程"], False

    if not candidates:
        return ["无满足覆盖要求的前继课程,即本课程为基础课程"], False

    # 按覆盖率和课程质量排序
    candidates.sort(reverse=True, key=lambda x: (x[0], -x[1].difficulty))
    top3 = [c[1] for c in candidates[:3]]

    return [c.name for c in top3], True


# --------------------------
# 执行入口
# --------------------------

def format_output(path, is_valid):
    """格式化输出结果"""
    if is_valid and len(path) > 1:
        return " → ".join(path[:-1]) + " --> " + path[-1]
    return path[0]


if __name__ == "__main__":
    try:
        # 示例测试（修改课程名称测试不同情况）
        course_name = "操作系统（自主模式）"
        target = Course.objects.get(name=course_name)

        # 生成推荐路径
        path, valid = generate_recommendation(target)

        # 格式化输出
        print("推荐路径:", format_output(path, valid))
    except ObjectDoesNotExist:
        print(f"错误：课程 {course_name} 不存在")
    except Exception as e:
        print(f"运行时错误: {str(e)}")