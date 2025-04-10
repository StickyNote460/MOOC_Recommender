# KGRS/kg_builder.py
import json
from django.db.models import Q
from recommender.models import (
    UserCourse, CourseConcept,
    PrerequisiteDependency, Course
)


def build_knowledge_graph():
    """构建知识图谱三元组（用户、课程、概念）"""
    kg_triples = []

    # 1. 用户-课程关系（selected_course）
    user_courses = UserCourse.objects.select_related('user', 'course').all()
    for uc in user_courses:
        kg_triples.append(
            (f"U_{uc.user_id}", "selected_course", f"C_{uc.course_id}")
        )

    # 2. 课程-核心概念关系（has_core_concept）
    course_concepts = CourseConcept.objects.all()
    for cc in course_concepts:
        kg_triples.append(
            (f"C_{cc.course_id}", "has_core_concept", f"K_{cc.concept_id}")
        )

    # 3. 概念间先修关系（concept_prerequisite）
    concept_relations = PrerequisiteDependency.objects.filter(
        Q(prerequisite__startswith="K_") & Q(target__startswith="K_")
    )
    for cr in concept_relations:
        kg_triples.append(
            (f"K_{cr.prerequisite}", "concept_prerequisite", f"K_{cr.target}")
        )

    return kg_triples


def save_kg_to_tsv(triples, file_path):
    """保存为TSV文件供TransE训练"""
    with open(file_path, 'w', encoding='utf-8') as f:
        for h, r, t in triples:
            f.write(f"{h}\t{r}\t{t}\n")