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
    """构建完整概念依赖图（显式添加所有概念节点）"""
    G = nx.DiGraph()

    # 强制添加所有概念节点（即使没有依赖关系）
    all_concepts = Concept.objects.all()
    for concept in all_concepts:
        G.add_node(concept.id)

    # 添加依赖边
    dependencies = PrerequisiteDependency.objects.select_related('prerequisite', 'target').all()
    for dep in dependencies:
        if dep.prerequisite.id in G and dep.target.id in G:
            G.add_edge(dep.prerequisite.id, dep.target.id)
        else:
            print(f"警告：依赖关系 {dep.prerequisite.id}→{dep.target.id} 包含无效概念，已忽略")

    return G


def generate_prerequisite_path(target_course):
    """生成目标课程的前置学习路径"""
    # 获取目标课程关联的所有概念
    course_concepts = target_course.concepts.all()
    concept_ids = [c.id for c in course_concepts]

    # 构建概念依赖图
    G = build_concept_graph()

    # 收集所有必需祖先概念
    required_concepts = set()
    for cid in concept_ids:
        if cid not in G:
            raise ValueError(f"概念 {cid} 未在知识图谱中定义")
        required_concepts.update(nx.ancestors(G, cid))

    # 获取覆盖这些概念的候选课程（排除目标课程）
    candidates = Course.objects.exclude(id=target_course.id).prefetch_related(
        Prefetch('concepts', queryset=Concept.objects.filter(id__in=required_concepts))
    ).distinct()

    # 构建课程依赖图
    course_G = nx.DiGraph()
    course_G.add_node(target_course.id)

    # 预加载课程概念映射
    course_concept_map = {
        c.id: set(c.concepts.values_list('id', flat=True))
        for c in candidates
    }

    # 建立课程间依赖关系
    for c1 in candidates:
        course_G.add_node(c1.id)
        for c2 in candidates:
            if c1.id == c2.id:
                continue
            # 检查c2是否依赖c1的概念
            for cid in course_concept_map[c2.id]:
                ancestors = nx.ancestors(G, cid)
                if any(a in course_concept_map[c1.id] for a in ancestors):
                    course_G.add_edge(c1.id, c2.id)
                    break

    # 添加目标课程依赖
    for c in candidates:
        if any(cid in required_concepts for cid in course_concept_map[c.id]):
            course_G.add_edge(c.id, target_course.id)

    # 拓扑排序
    try:
        sorted_ids = list(nx.topological_sort(course_G))
    except nx.NetworkXUnfeasible:
        return ["检测到循环依赖，请检查课程设置！"]

    # 映射课程ID到名称
    id_to_name = {c.id: c.name for c in candidates}
    id_to_name[target_course.id] = target_course.name

    # 过滤并生成路径
    path = []
    for cid in sorted_ids:
        if cid == target_course.id and len(path) > 0:  # 目标课程放在最后
            continue
        if cid in id_to_name:
            path.append(id_to_name[cid])

    # 添加目标课程到末尾
    path.append(target_course.name)

    return path


if __name__ == "__main__":
    try:
        target_course = Course.objects.get(name="数据结构(上)(自主模式)")
        path = generate_prerequisite_path(target_course)
        print("推荐路径:", " → ".join(path))
    except Course.DoesNotExist:
        print("错误：测试课程不存在")
    except Exception as e:
        print("运行错误:", str(e))