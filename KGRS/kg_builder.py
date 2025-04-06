# KGRS/kg_builder.py
import os
import sys
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recommender.models import (
    CourseConcept,
    PrerequisiteDependency,
    UserCourse,
    Course,
    Concept
)
def build_knowledge_graph():
    """
    构建知识图谱三元组（基于最新数据结构）
    返回格式: [(head, relation, tail), ...]
    """
    kg_triples = []

    # 1. 课程-核心概念关系（来自CourseConcept表）
    for cc in CourseConcept.objects.select_related('course', 'concept'):
        kg_triples.append(
            (f"C_{cc.course.id}", "has_core_concept", f"K_{cc.concept.id}")
        )

    # 2. 概念间先修关系（来自PrerequisiteDependency表）
    for pd in PrerequisiteDependency.objects.select_related('prerequisite', 'target'):
        kg_triples.append(
            (f"K_{pd.prerequisite.id}", "concept_prerequisite", f"K_{pd.target.id}")
        )

    # 3. 用户-课程关系（来自UserCourse表）
    for uc in UserCourse.objects.select_related('user', 'course'):
        kg_triples.append(
            (f"U_{uc.user.id}", "selected_course", f"C_{uc.course.id}")
        )

    return kg_triples


def save_kg(kg_triples, file_path):
    """保存知识图谱到文件"""
    with open(file_path, 'w') as f:
        for h, r, t in kg_triples:
            f.write(f"{h}\t{r}\t{t}\n")