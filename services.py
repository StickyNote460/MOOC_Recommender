import networkx as nx
from django.db.models import Prefetch
import logging

import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MOOC_Recommender.settings')
django.setup()
from recommender.models import Course, Concept, PrerequisiteDependency, CourseConcept

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_concept_graph():
    """构建概念依赖图（prerequisite -> target）"""
    G = nx.DiGraph()
    deps = PrerequisiteDependency.objects.select_related('prerequisite', 'target').all()
    for dep in deps:
        G.add_edge(dep.prerequisite.id, dep.target.id)
    return G


def generate_prerequisite_path(target_course):
    """生成目标课程的前置学习路径"""
    try:
        # 获取目标课程关联的概念
        course_concepts = target_course.concepts.all()
        concept_ids = [c.id for c in course_concepts]

        # 构建概念依赖图并收集所有祖先概念
        G = build_concept_graph()
        required_concepts = set()
        for cid in concept_ids:
            required_concepts.update(nx.ancestors(G, cid))

        # 获取覆盖这些概念的候选课程（排除目标课程）
        candidates = Course.objects.exclude(id=target_course.id).prefetch_related(
            Prefetch('concepts', queryset=Concept.objects.filter(id__in=required_concepts))
        ).distinct()

        # 构建课程依赖图
        course_G = nx.DiGraph()
        course_G.add_node(target_course.id)

        # 预加载课程概念映射
        course_concept_map = {c.id: set(c.concepts.values_list('id', flat=True)) for c in candidates}

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
            logger.error("检测到循环依赖！")
            return {"error": "检测到循环依赖！"}

        # 映射课程ID到名称
        id_to_name = {c.id: c.name for c in candidates}
        id_to_name[target_course.id] = target_course.name
        path = [id_to_name[cid] for cid in sorted_ids if cid != target_course.id]
        path.append(target_course.name)

        return path

    except Exception as e:
        logger.error(f"运行错误: {str(e)}")
        return {"error": str(e)}


if __name__ == "__main__":
    try:
        target_course = Course.objects.get(name="数据结构(上)(自主模式)")  # 确保数据库中存在该课程
        path = generate_prerequisite_path(target_course)
        print("推荐路径:", " → ".join(path) if isinstance(path, list) else path)
    except Course.DoesNotExist:
        print("错误：测试课程不存在")