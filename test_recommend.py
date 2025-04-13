import traceback
from django.core.exceptions import ObjectDoesNotExist
from services import generate_recommendation, format_output, RecommendationError, CourseNotFoundError
import os
import django
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MOOC_Recommender.settings')
django.setup()
from recommender.models import Course, Concept, PrerequisiteDependency

def run_test(test_func, test_name):
    """执行测试并处理异常"""
    try:
        test_func()
        print(f"[成功] {test_name}")
    except ObjectDoesNotExist as e:
        print(f"\n[失败] {test_name} - 数据库查询失败: {str(e)}")
        traceback.print_exc()
    except CourseNotFoundError as e:
        print(f"\n[失败] {test_name} - 课程不存在: {e.course_name}")
    except RecommendationError as e:
        print(f"\n[失败] {test_name} - 推荐逻辑错误: {str(e)}")
    except Exception as e:
        print(f"\n[严重错误] {test_name} - 未捕获异常: {str(e)}")
        traceback.print_exc()

def test_valid_recommendation():
    """测试有效推荐场景"""
    target = Course.objects.get(name="操作系统（自主模式）")
    pre_courses, valid, target_name = generate_recommendation(target)
    output = format_output(pre_courses, valid, target_name)
    assert "数据结构" in output, "预期结果未包含必要前继课程"

def test_course_not_found():
    """测试课程不存在场景"""
    try:
        Course.objects.get(name="不存在的课程")
    except ObjectDoesNotExist:
        raise CourseNotFoundError("不存在的课程")

if __name__ == "__main__":
    print("\n========== 开始测试 =========")
    run_test(test_valid_recommendation, "有效推荐测试")
    run_test(test_course_not_found, "课程不存在测试")
    print("\n========== 测试结束 =========")