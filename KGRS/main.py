# KGRS/main.py
import os
import sys
import django
import torch
from pathlib import Path

# 环境初始化
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MOOC_Recommender.settings')
django.setup()

from kg_builder import build_knowledge_graph, save_kg_to_tsv
from transE import train_transE
from mkr import MKR


def generate_recommendation(user_id, target_course_id, transE_model, entity2id):
    """生成个性化学习路径"""
    # 1. 获取用户已学课程
    from recommender.models import UserCourse
    user_courses = UserCourse.objects.filter(user_id=user_id).values_list('course_id', flat=True)

    # 2. 获取目标课程的所有先修概念
    from recommender.models import CourseConcept, PrerequisiteDependency
    target_concepts = CourseConcept.objects.filter(course_id=target_course_id).values_list('concept_id', flat=True)

    # 3. 拓扑排序生成学习路径（示例逻辑）
    learning_path = []
    for concept_id in target_concepts:
        # 获取概念的所有先修概念
        prerequisites = PrerequisiteDependency.objects.filter(target=concept_id).values_list('prerequisite', flat=True)
        # 添加未学习的先修概念
        for pre in prerequisites:
            if pre not in learning_path:
                learning_path.append(pre)
        learning_path.append(concept_id)

    # 4. 将概念路径转换为课程推荐
    recommended_courses = []
    for concept in learning_path:
        courses = CourseConcept.objects.filter(concept_id=concept).exclude(course_id__in=user_courses)
        recommended_courses.extend([c.course_id for c in courses])

    return recommended_courses[:10]  # 返回前10个推荐课程


if __name__ == "__main__":
    # 1. 构建知识图谱
    kg_triples = build_knowledge_graph()
    save_kg_to_tsv(kg_triples, BASE_DIR / "data/kg_triples.tsv")

    # 2. 训练TransE模型
    transE_model, entity2id, _ = train_transE(kg_triples)

    # 3. 示例推荐
    user_id = "U_7001215"
    target_course_id = "C_course-v1:McGillX+ATOC185x+2015_T1"
    recommendations = generate_recommendation(user_id, target_course_id, transE_model, entity2id)
    print(f"用户 {user_id} 的学习路径推荐：{recommendations}")