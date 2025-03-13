from django.db import models

# Create your models here.
# recommender/models.py
from django.db import models

class School(models.Model):
    id = models.CharField(
        max_length=50,
        primary_key=True,
        verbose_name="学校ID"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="学校名称"
    )
    about = models.TextField(
        verbose_name="学校简介",
        blank=True  # 允许空值
    )

    class Meta:
        verbose_name = "学校"  # 后台显示名称
        verbose_name_plural = "学校列表"  # 复数形式

    def __str__(self):
        return self.name  # 后台显示友好名称