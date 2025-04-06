
# Create your models here.
# recommender/models.py
from django.db import models
import uuid

# 核心实体模型
class Concept(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=200)
    explanation = models.TextField(blank=True, null=True)

class Course(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=200)
    prerequisites = models.TextField(blank=True, null=True)  # 原JSONField改为TextField（示例中值为"无。"）
    #prerequisites = models.JSONField(blank=True, null=True)  # 存储先修课程列表
    core_concept = models.ForeignKey(Concept, on_delete=models.SET_NULL, null=True)
    video_order = models.JSONField(blank=True, null=True)    # 新增video_order字段（根据course.json示例）
    chapter = models.JSONField(blank=True, null=True)        # 新增章节结构字段

class Video(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=200)
    start = models.JSONField(blank=True, null=True)  # 时间戳数组（如 [39460, 43010, ...]）
    end = models.JSONField(blank=True, null=True)    # 时间戳数组
    text = models.TextField(blank=True, null=True)

class User(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    course_order = models.JSONField(blank=True, null=True)  # 用户已选课程顺序（列表）
    enroll_time = models.JSONField(blank=True, null=True)    # 注册时间列表（新增字段）
# 关键关系模型
class PrerequisiteDependency(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="前置关系ID"
    )
    prerequisite = models.CharField(max_length=200)  # 改为CharField（示例中直接存储概念ID字符串）
    target = models.CharField(max_length=200)        # 如 "K_计算机科学_计算机科学技术"
    # 或保持外键但需处理复合键：
    # prerequisite = models.ForeignKey(Concept, on_delete=models.CASCADE, to_field='id')

class CourseConcept(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="关系ID"
    )
    course_id = models.CharField(max_length=100)
    concept_id = models.CharField(max_length=100)

class UserCourse(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="用户课程关系ID"
    )
    user_id = models.CharField(max_length=100)  # 如 "U_7001215"
    course_id = models.CharField(max_length=100) # 如 "C_course-v1:TsinghuaX+00740043_2x_2015_T2+sp"
"""class CourseConcept(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)

class PrerequisiteDependency(models.Model):
    prerequisite = models.ForeignKey(Concept, related_name='prereq', on_delete=models.CASCADE)
    target = models.ForeignKey(Concept, related_name='target', on_delete=models.CASCADE)

class UserCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
"""
####################
class School(models.Model):
    # 定义School模型的字段
    id = models.CharField(
        max_length=50,
        primary_key=True,
        verbose_name="学校ID"  # 在Django后台显示的字段名称
    )
    name = models.CharField(
        max_length=200,
        verbose_name="学校名称"
    )
    about = models.TextField(
        verbose_name="学校简介",
        blank=True  # 允许该字段为空
    )

    # 定义模型的Meta类，用于设置一些额外的选项
    class Meta:
        verbose_name = "学校"  # 在Django后台显示的模型名称（单数）
        verbose_name_plural = "学校列表"  # 在Django后台显示的模型名称（复数）

    # 定义__str__方法，用于指定在Django后台或管理界面中显示模型的哪个字段
    def __str__(self):
        return self.name