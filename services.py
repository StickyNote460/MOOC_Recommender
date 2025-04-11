# services.py（根目录）
import os
import django
import sys
import networkx as nx
from django.db.models import Prefetch

# 初始化 Django 环境
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MOOC_Recommender.settings')
django.setup()

from recommender.models import Course, Concept, PrerequisiteDependency, CourseConcept


def build_concept_graph():
    """构建概念依赖图（包含所有概念及其依赖关系）"""
    G = nx.DiGraph()
    # 添加所有概念节点
    all_concepts = Concept.objects.all()
    for concept in all_concepts:
        G.add_node(concept.id)
    # 添加依赖边
    for dep in PrerequisiteDependency.objects.select_related('prerequisite', 'target').all():
        if dep.prerequisite.id in G and dep.target.id in G:
            G.add_edge(dep.prerequisite.id, dep.target.id)
    return G


def get_required_prerequisites(target_course):
    """获取目标课程所需的所有前驱概念（递归祖先）"""
    # 获取目标课程直接关联的概念
    target_concepts = set(target_course.concepts.values_list('id', flat=True))

    # 构建概念依赖图
    G = build_concept_graph()

    # 收集所有祖先概念
    required_concepts = set()
    for cid in target_concepts:
        required_concepts.update(nx.ancestors(G, cid))

    return required_concepts


def recommend_top3_courses(required_concepts, exclude_course_id):
    """推荐覆盖最多前驱概念的前三门课程（无需排序）"""
    # 获取候选课程（排除目标课程自身）
    candidates = Course.objects.exclude(id=exclude_course_id).prefetch_related('concepts')

    # 计算每个课程覆盖的前驱概念数量
    course_scores = []
    for course in candidates:
        course_concepts = set(course.concepts.values_list('id', flat=True))
        overlap = len(course_concepts & required_concepts)
        if overlap > 0:
            course_scores.append((overlap, course))

    # 按覆盖数降序排序，取前三
    course_scores.sort(reverse=True, key=lambda x: x[0])
    top3 = [course for _, course in course_scores[:3]]

    return top3


def generate_path(target_course):
    """生成推荐路径：C1, C2, C3 --> Origin"""
    # 获取所有必需前驱概念
    required_concepts = get_required_prerequisites(target_course)

    # 推荐前三课程
    top3 = recommend_top3_courses(required_concepts, target_course.id)

    if not top3:
        return [target_course.name]

    # 生成路径（前三课程集合 + 目标课程）
    path = [course.name for course in top3]
    path.append(target_course.name)
    return path


if __name__ == "__main__":
    try:
        target_course = Course.objects.get(name="编译技术")
        path = generate_path(target_course)
        print("推荐路径:", " , ".join(path[:-1]) + " ---> " + path[-1])
    except Course.DoesNotExist:
        print("错误：课程不存在")
    except Exception as e:
        print("运行错误:", str(e))