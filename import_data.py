# MOOC_Recommender/import_data.py
import json
import logging
import os
from pathlib import Path

from django.core.management.base import BaseCommand

import django
from django.conf import settings

# --------------------------
# 1. Django环境初始化配置
# --------------------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MOOC_Recommender.settings')
django.setup()

# --------------------------
# 2. 模型导入
# --------------------------
from recommender.models import (
    Concept, Course, Video, User,
    PrerequisiteDependency, CourseConcept, UserCourse
)

# --------------------------
# 3. 日志配置
# --------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class Command(BaseCommand):
    help = 'Import MOOCCube dataset into Django models'

    def handle(self, *args, **options):
        """主处理函数"""
        # 项目根目录：MOOC_Recommender/
        project_root = Path(__file__).resolve().parent

        # 数据集路径：MOOC_Recommender/MOOCCube/
        base_path = project_root / "MOOCCube"

        self.stdout.write("🔄 开始数据导入流程...")

        # --------------------------
        # 4. 按顺序导入数据
        # --------------------------
        # 先导入基础实体
        self.import_data(
            "概念数据", base_path / "entities/concept.json", self.import_concepts
        )
        self.import_data(
            "课程数据", base_path / "entities/course.json", self.import_courses
        )
        self.import_data(
            "视频数据", base_path / "entities/video.json", self.import_videos
        )
        self.import_data(
            "用户数据", base_path / "entities/user.json", self.import_users
        )

        # 再导入关系数据
        self.import_data(
            "先修关系", base_path / "relations/prerequisite-dependency.json", self.import_prerequisite_deps
        )
        self.import_data(
            "课程-概念", base_path / "relations/course-concept.json", self.import_course_concepts
        )
        self.import_data(
            "用户-课程", base_path / "relations/user-course.json", self.import_user_courses
        )

        self.stdout.write("✅ 数据导入完成！")

    # --------------------------
    # 通用辅助方法
    # --------------------------
    def import_data(self, data_type, file_path, handler):
        """通用数据导入包装器"""
        self.stdout.write(f"⏳ 正在导入 {data_type} ({file_path})...")
        try:
            # 获取当前记录数用于统计
            count_before = self.get_model_count(handler)

            # 执行具体导入方法
            handler(file_path)

            # 计算并显示导入数量
            count_after = self.get_model_count(handler)
            delta = count_after - count_before
            self.stdout.write(
                f"✔️ 成功导入 {delta} 条{data_type}记录"
                if delta > 0
                else f"⚠️ 未发现新{data_type}记录"
            )
        except FileNotFoundError:
            logger.error(f"文件不存在：{file_path}")
            self.stdout.write(self.style.ERROR(f"❌ 文件未找到：{file_path}"))
        except Exception as e:
            logger.error(f"导入{data_type}失败: {str(e)}")
            self.stdout.write(self.style.ERROR(f"❌ {data_type}导入失败！"))

    def get_model_count(self, handler):
        """获取模型当前记录数"""
        model_map = {
            self.import_concepts: Concept,
            self.import_courses: Course,
            self.import_videos: Video,
            self.import_users: User,
            self.import_prerequisite_deps: PrerequisiteDependency,
            self.import_course_concepts: CourseConcept,
            self.import_user_courses: UserCourse,
        }
        return model_map[handler].objects.count() if handler in model_map else 0

    # --------------------------
    # 实体数据导入方法
    # --------------------------
    def import_concepts(self, file_path):
        """导入概念数据（每行一个JSON对象）"""
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    Concept.objects.update_or_create(
                        id=data['id'],
                        defaults={
                            'name': data.get('name', ''),
                            'en': data.get('en', ''),
                            'explanation': data.get('explanation', '暂无说明')
                        }
                    )
                    # 每处理100条显示进度
                    if line_num % 100 == 0:
                        self.stdout.write(f"  已处理 {line_num} 条概念记录...")
                except json.JSONDecodeError as e:
                    logger.error(f"行{line_num} JSON解析失败: {str(e)}")
                except KeyError as e:
                    logger.error(f"行{line_num} 缺少必要字段: {str(e)}")
                except Exception as e:
                    logger.error(f"行{line_num} 概念导入失败: {str(e)}")

    def import_courses(self, file_path):
        """导入课程数据（每行一个JSON对象）"""
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)

                    # 清洗先修条件字段
                    raw_prerequisites = data.get('prerequisites', '无。')
                    prerequisites = (
                        [] if raw_prerequisites == '无。'
                        else json.loads(raw_prerequisites)
                    )

                    # 处理核心概念外键
                    core_concept = None
                    if (core_id := data.get('core_id')) and Concept.objects.filter(id=core_id).exists():  # 移除多余右括号
                        core_concept = Concept.objects.get(id=core_id)

                    # 创建/更新课程记录
                    Course.objects.update_or_create(
                        id=data['id'],
                        defaults={
                            'name': data['name'],
                            'prerequisites': prerequisites,
                            'core_concept': core_concept,
                            'video_order': data.get('video_order', []),
                            'chapter': data.get('chapter', [])
                        }
                    )

                    # 每处理50条显示进度
                    if line_num % 50 == 0:
                        self.stdout.write(f"  已处理 {line_num} 条课程记录...")
                except json.JSONDecodeError as e:
                    logger.error(f"行{line_num} JSON解析失败: {str(e)}")
                except KeyError as e:
                    logger.error(f"行{line_num} 缺少必要字段: {str(e)}")
                except Exception as e:
                    logger.error(f"行{line_num} 课程导入失败: {str(e)}")

    def import_videos(self, file_path):
        """导入视频数据（每行一个JSON对象）"""
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    Video.objects.update_or_create(
                        id=data['id'],
                        defaults={
                            'name': data['name'],
                            'start': data.get('start', []),
                            'end': data.get('end', []),
                            'text': data.get('text', '')
                        }
                    )
                    # 每处理200条显示进度
                    if line_num % 200 == 0:
                        self.stdout.write(f"  已处理 {line_num} 条视频记录...")
                except json.JSONDecodeError as e:
                    logger.error(f"行{line_num} JSON解析失败: {str(e)}")
                except KeyError as e:
                    logger.error(f"行{line_num} 缺少必要字段: {str(e)}")
                except Exception as e:
                    logger.error(f"行{line_num} 视频导入失败: {str(e)}")

    def import_users(self, file_path):
        """导入用户数据（每行一个JSON对象）"""
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    User.objects.update_or_create(
                        id=data['id'],
                        defaults={
                            'name': data['name'],
                            'course_order': data.get('course_order', []),
                            'enroll_time': data.get('enroll_time', [])
                        }
                    )
                    # 每处理500条显示进度
                    if line_num % 500 == 0:
                        self.stdout.write(f"  已处理 {line_num} 条用户记录...")
                except json.JSONDecodeError as e:
                    logger.error(f"行{line_num} JSON解析失败: {str(e)}")
                except KeyError as e:
                    logger.error(f"行{line_num} 缺少必要字段: {str(e)}")
                except Exception as e:
                    logger.error(f"行{line_num} 用户导入失败: {str(e)}")

    # --------------------------
    # 关系数据导入方法
    # --------------------------
    def import_prerequisite_deps(self, file_path):
        """导入先修关系（每行格式：prerequisite\target）"""
        with open(file_path, 'r', encoding='utf-8') as f:
            batch = []
            total_processed = 0
            for line_num, line in enumerate(f, 1):
                try:
                    # 分割字段
                    prerequisite, target = line.strip().split('\t')

                    # 创建对象实例
                    batch.append(PrerequisiteDependency(
                        prerequisite=prerequisite,
                        target=target
                    ))

                    # 批量插入（每1000条）
                    if len(batch) >= 1000:
                        PrerequisiteDependency.objects.bulk_create(batch)
                        total_processed += len(batch)
                        batch = []
                        self.stdout.write(f"  已批量插入 {total_processed} 条先修关系...")
                except ValueError:
                    logger.error(f"行{line_num} 格式错误，需要两个字段")
                except Exception as e:
                    logger.error(f"行{line_num} 先修关系导入失败: {str(e)}")

            # 插入剩余数据
            if batch:
                PrerequisiteDependency.objects.bulk_create(batch)
                self.stdout.write(f"  最后批量插入 {len(batch)} 条先修关系")

    def import_course_concepts(self, file_path):
        """导入课程-概念关系（每行格式：course_id\tconcept_id）"""
        with open(file_path, 'r', encoding='utf-8') as f:
            batch = []
            total_processed = 0
            for line_num, line in enumerate(f, 1):
                try:
                    # 分割字段
                    course_id, concept_id = line.strip().split('\t')

                    # 验证外键存在性
                    if not Course.objects.filter(id=course_id).exists():
                        logger.warning(f"行{line_num} 课程不存在: {course_id}")
                        continue
                    if not Concept.objects.filter(id=concept_id).exists():
                        logger.warning(f"行{line_num} 概念不存在: {concept_id}")
                        continue

                    # 创建对象实例
                    batch.append(CourseConcept(
                        course_id=course_id,
                        concept_id=concept_id
                    ))

                    # 批量插入（每1000条）
                    if len(batch) >= 1000:
                        CourseConcept.objects.bulk_create(batch)
                        total_processed += len(batch)
                        batch = []
                        self.stdout.write(f"  已批量插入 {total_processed} 条课程-概念关系...")
                except ValueError:
                    logger.error(f"行{line_num} 格式错误，需要两个字段")
                except Exception as e:
                    logger.error(f"行{line_num} 课程-概念关系导入失败: {str(e)}")

            # 插入剩余数据
            if batch:
                CourseConcept.objects.bulk_create(batch)
                self.stdout.write(f"  最后批量插入 {len(batch)} 条课程-概念关系")

    def import_user_courses(self, file_path):
        """导入用户-课程关系（每行格式：user_id\tcourse_id）"""
        with open(file_path, 'r', encoding='utf-8') as f:
            batch = []
            total_processed = 0
            for line_num, line in enumerate(f, 1):
                try:
                    # 分割字段
                    user_id, course_id = line.strip().split('\t')

                    # 验证外键存在性
                    if not User.objects.filter(id=user_id).exists():
                        logger.warning(f"行{line_num} 用户不存在: {user_id}")
                        continue
                    if not Course.objects.filter(id=course_id).exists():
                        logger.warning(f"行{line_num} 课程不存在: {course_id}")
                        continue

                    # 创建对象实例
                    batch.append(UserCourse(
                        user_id=user_id,
                        course_id=course_id
                    ))

                    # 批量插入（每1000条）
                    if len(batch) >= 1000:
                        UserCourse.objects.bulk_create(batch)
                        total_processed += len(batch)
                        batch = []
                        self.stdout.write(f"  已批量插入 {total_processed} 条用户-课程关系...")
                except ValueError:
                    logger.error(f"行{line_num} 格式错误，需要两个字段")
                except Exception as e:
                    logger.error(f"行{line_num} 用户-课程关系导入失败: {str(e)}")

            # 插入剩余数据
            if batch:
                UserCourse.objects.bulk_create(batch)
                self.stdout.write(f"  最后批量插入 {len(batch)} 条用户-课程关系")


# --------------------------
# 执行说明
# --------------------------
"""
运行步骤：
1. 确保项目结构符合以下要求：
   MOOC_Recommender/
   ├── MOOCCube/
   │   ├── entities/
   │   │   ├── concept.json
   │   │   ├── course.json
   │   │   ├── user.json
   │   │   └── video.json
   │   └── relations/
   │       ├── prerequisite-dependency.json
   │       ├── course-concept.json
   │       └── user-course.json
   ├── manage.py
   └── import_data.py

2. 在项目根目录执行：
   python manage.py import_data

3. 观察控制台输出：
   - 绿色对勾表示成功
   - 红色叉号表示失败
   - 黄色警告表示数据问题

4. 检查日志：
   - 所有错误详细信息会记录在日志中
   - 推荐配置日志文件（修改logging.basicConfig）
"""