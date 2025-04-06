# kg_construction.py
import json
from django.db.models import Q
from recommender.models import (
    User, Course, Concept,
    UserCourse, PrerequisiteDependency,
    CourseConcept
)


def build_knowledge_graph():
    """
    构建知识图谱的核心函数，返回四类关系的三元组列表
    返回格式: [(头实体, 关系, 尾实体), ...]
    """
    kg_triples = []

    # --------------------------
    # 1. 用户选修课程关系 (用户 selected_course 课程)
    # --------------------------
    # 从UserCourse关系表中获取所有用户-课程选课记录
    user_courses = UserCourse.objects.all()
    for uc in user_courses:
        kg_triples.append(
            (f"U_{uc.user_id}", "selected_course", f"C_{uc.course_id}")
        )

    # --------------------------
    # 2. 课程间前后修关系 (课程A course_prerequisite 课程B)
    # --------------------------
    # 方案一：如果课程模型有明确的prerequisites字段（需确保存储的是课程ID列表）
    courses = Course.objects.exclude(prerequisites__isnull=True)
    for course in courses:
        # 假设prerequisites字段存储的是JSON数组，如 ["C_101", "C_102"]
        if course.prerequisites and course.prerequisites != "无":
            try:
                prereqs = json.loads(course.prerequisites)
                for prereq_id in prereqs:
                    kg_triples.append(
                        (f"C_{prereq_id}", "course_prerequisite", f"C_{course.id}")
                    )
            except json.JSONDecodeError:
                pass

    # 方案二：如果使用单独的PrerequisiteDependency模型（需调整模型指向课程）
    # for pd in PrerequisiteDependency.objects.all():
    #     kg_triples.append(
    #         (f"C_{pd.prerequisite}", "course_prerequisite", f"C_{pd.target}")
    #     )

    # --------------------------
    # 3. 课程核心概念关系 (课程 has_core_concept 概念)
    # --------------------------
    # 从Course模型的core_concept外键获取
    courses_with_concept = Course.objects.exclude(core_concept__isnull=True)
    for course in courses_with_concept:
        kg_triples.append(
            (f"C_{course.id}", "has_core_concept", f"K_{course.core_concept.id}")
        )

    # --------------------------
    # 4. 概念间前后继关系 (概念A concept_prerequisite 概念B)
    # --------------------------
    # 假设存在ConceptPrerequisite模型存储概念间关系
    # 这里用PrerequisiteDependency模型示例（需确保存储的是概念ID）
    concept_prereqs = PrerequisiteDependency.objects.filter(
        Q(prerequisite__startswith="K_") & Q(target__startswith="K_")
    )
    for cp in concept_prereqs:
        kg_triples.append(
            (f"K_{cp.prerequisite}", "concept_prerequisite", f"K_{cp.target}")
        )

    return kg_triples


def save_kg_to_file(triples, filename):
    """
    将知识图谱保存为JSON文件
    :param triples: 三元组列表
    :param filename: 输出文件名
    """
    formatted = [
        {"head": h, "relation": r, "tail": t}
        for h, r, t in triples
    ]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(formatted, f, ensure_ascii=False, indent=2)


def validate_kg(triples):
    """
    知识图谱基础验证
    :return: 验证结果字典
    """
    # 统计各关系数量
    relation_counts = {}
    for _, r, _ in triples:
        relation_counts[r] = relation_counts.get(r, 0) + 1

    # 检查空值
    invalid = [t for t in triples if not all(t)]

    return {
        "total_triples": len(triples),
        "relation_distribution": relation_counts,
        "invalid_count": len(invalid)
    }


if __name__ == "__main__":
    # 步骤1：构建知识图谱
    kg_data = build_knowledge_graph()

    # 步骤2：验证数据完整性
    validation = validate_kg(kg_data)
    print(f"知识图谱验证结果：\n{json.dumps(validation, indent=2)}")

    # 步骤3：保存为文件
    save_kg_to_file(kg_data, "knowledge_graph.json")
    print("知识图谱已保存到 knowledge_graph.json")