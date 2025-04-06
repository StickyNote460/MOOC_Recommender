import json  # 用于处理JSON数据
import os  # 用于处理文件和目录路径
import django  # 导入Django框架
from django.conf import settings  # 从Django配置中导入settings模块，用于访问项目设置
# 设置 DJANGO_SETTINGS_MODULE 环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MOOC_Recommender.settings')
# 加载 Django 项目配置，可使用Django的ORM等功能
django.setup()

# 从recommender应用的models.py中导入School模型
from recommender.models import School

#定义数据导入函数
#函数定义 def function_name(parameters): body return value
def import_schools():
    # 使用os.path.join构建相对于settings.BASE_DIR的路径，指向school.json文件
    json_path = os.path.join(settings.BASE_DIR, 'MOOCCube', 'entities', 'school.json')

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            # 逐行读取文件
            for line in f:
                # 将每一行JSON字符串解析为Python字典
                school_data = json.loads(line)
                # 使用update_or_create方法创建或更新School记录
                # 如果School表中已存在具有相同id的记录，则更新其name和about字段（如果提供了新值）
                # 如果不存在，则创建新记录
                School.objects.update_or_create(
                    id=school_data['id'],#一个条件，根据这条语句来更新或创建一个对象。
                    defaults={
                        'name': school_data['name'],
                        'about': school_data.get('about', '')  # 如果JSON中没有about字段，则使用空字符串作为默认值
                    }
                )
        # 导入完成后，打印School表中的记录总数
        print("学校数据导入完成！共导入{}条数据".format(School.objects.count()))
    except FileNotFoundError:
        # 如果文件未找到，则打印错误消息
        print(f"文件 {json_path} 未找到。")
    except json.JSONDecodeError:
        # 如果JSON解码失败（例如，由于格式错误），则打印错误消息
        print("JSON 解码错误。请检查文件内容是否有效。")
    except Exception as e:
        # 捕获其他所有异常，并打印错误消息
        print(f"发生错误：{e}")

# 调用函数以导入数据
import_schools()