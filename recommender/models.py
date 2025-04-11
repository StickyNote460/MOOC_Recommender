# recommender/models.py
from django.db import models

class Concept(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    explanation = models.TextField()

class Course(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    prerequisites = models.TextField()
    # 关键修正
    concepts = models.ManyToManyField(Concept, through='CourseConcept')

class User(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    course_order = models.JSONField()
    enroll_time = models.JSONField()

class CourseConcept(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=40,
        editable=False
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)

class PrerequisiteDependency(models.Model):
    prerequisite = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='prerequisite_relations')
    target = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='target_relations')

class UserCourse(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=40,
        editable=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)