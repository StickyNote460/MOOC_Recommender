import json
import os
import django
from django.conf import settings  # 取消注释以导入 settings

# 设置 DJANGO_SETTINGS_MODULE 环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MOOC_Recommender.settings')
# 加载 Django 项目配置
django.setup()

from recommender.models import School


def import_schools():
    # 使用 os.path.join 构建相对于 settings.BASE_DIR 的路径
    json_path = os.path.join(settings.BASE_DIR, 'MOOCCube', 'entities', 'school.json')

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            for line in f:
                school_data = json.loads(line)
                # 创建或更新记录
                School.objects.update_or_create(
                    id=school_data['id'],
                    defaults={
                        'name': school_data['name'],
                        'about': school_data.get('about', '')  # 处理可能的缺失字段
                    }
                )
        print("学校数据导入完成！共导入{}条数据".format(School.objects.count()))
    except FileNotFoundError:
        print(f"文件 {json_path} 未找到。")
    except json.JSONDecodeError:
        print("JSON 解码错误。请检查文件内容是否有效。")
    except Exception as e:
        print(f"发生错误：{e}")


# 调用函数以导入数据
import_schools()