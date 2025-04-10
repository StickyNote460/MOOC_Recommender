import os
import json
import django
from django.db import transaction

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MOOC_Recommender.settings')
django.setup()

from recommender.models import CourseConcept, UserCourse, Course, Concept, User

DATA_ROOT = "MOOCCube/relations"


def import_course_concept():
    """导入课程-知识点关系数据"""
    filepath = os.path.join(DATA_ROOT, "course-concept_fixed.json")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = len(data)
    success = 0
    skipped = 0
    errors = []

    print(f"\n开始导入课程-知识点关系（共 {total} 条）")

    for idx, item in enumerate(data, 1):
        try:
            with transaction.atomic():
                # 检查是否已存在
                if CourseConcept.objects.filter(id=item['id']).exists():
                    print(f"[{idx}/{total}] 已跳过已存在记录：{item['id']}")
                    skipped += 1
                    continue

                # 获取关联对象
                course = Course.objects.get(id=item['prerequisite'])
                concept = Concept.objects.get(id=item['target'])

                # 创建记录
                CourseConcept.objects.create(
                    id=item['id'],
                    course=course,
                    concept=concept
                )

                success += 1
                print(f"[{idx}/{total}] 成功导入：{item['id']}")

        except Course.DoesNotExist:
            errors.append(f"课程不存在：{item['prerequisite']}（ID：{item['id']}）")
        except Concept.DoesNotExist:
            errors.append(f"知识点不存在：{item['target']}（ID：{item['id']}）")
        except Exception as e:
            errors.append(f"未知错误：{str(e)}（ID：{item['id']}）")

    print(f"\n导入完成！成功：{success}，跳过：{skipped}，失败：{len(errors)}")
    if errors:
        print("\n错误列表：")
        for error in errors[-5:]:  # 显示最后5个错误
            print(f"• {error}")


def import_user_course():
    """导入用户-课程关系数据"""
    filepath = os.path.join(DATA_ROOT, "user-course_fixed.json")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = len(data)
    success = 0
    skipped = 0
    errors = []

    print(f"\n开始导入用户-课程关系（共 {total} 条）")

    for idx, item in enumerate(data, 1):
        try:
            with transaction.atomic():
                # 检查是否已存在
                if UserCourse.objects.filter(id=item['id']).exists():
                    print(f"[{idx}/{total}] 已跳过已存在记录：{item['id']}")
                    skipped += 1
                    continue

                # 获取关联对象
                user = User.objects.get(id=item['prerequisite'])
                course = Course.objects.get(id=item['target'])

                # 创建记录
                UserCourse.objects.create(
                    id=item['id'],
                    user=user,
                    course=course
                )

                success += 1
                print(f"[{idx}/{total}] 成功导入：{item['id']}")

        except User.DoesNotExist:
            errors.append(f"用户不存在：{item['prerequisite']}（ID：{item['id']}）")
        except Course.DoesNotExist:
            errors.append(f"课程不存在：{item['target']}（ID：{item['id']}）")
        except Exception as e:
            errors.append(f"未知错误：{str(e)}（ID：{item['id']}）")

    print(f"\n导入完成！成功：{success}，跳过：{skipped}，失败：{len(errors)}")
    if errors:
        print("\n错误列表：")
        for error in errors[-5:]:
            print(f"• {error}")


if __name__ == "__main__":
    import_course_concept()
    import_user_course()
    print("\n全部数据导入完成！")