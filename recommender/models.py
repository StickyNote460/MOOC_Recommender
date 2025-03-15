from django.db import models

# Create your models here.
# recommender/models.py
from django.db import models

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