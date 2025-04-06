import json
import uuid
from pathlib import Path

RELATION_FILES = [
    "MOOCCUBE/relations/prerequisite-dependency.json",
    "MOOCCUBE/relations/course-concept.json",
    "MOOCCUBE/relations/user-course.json"
]

def convert_relation_file(input_path, relation_type="default"):
    """
    转换关系文件为标准JSON格式
    :param input_path: 输入文件路径
    :param relation_type: 关系类型标识（用于生成语义化ID）
    :return: 转换是否成功
    """
    # 路径处理
    input_path = Path(input_path)
    output_path = input_path.with_name(input_path.stem + "_fixed.json")

    # 生成ID的前缀
    type_prefix = {
        "prerequisite-dependency": "PRE",
        "course-concept": "CC",
        "user-course": "UC"
    }.get(input_path.stem, "REL")

    relations = []
    line_count = 0
    success_count = 0

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_count += 1
                line = line.strip()
                if not line:
                    continue

                # 分割字段（支持制表符和空格）
                parts = line.replace('\t', ' ').split()
                if len(parts) != 2:
                    print(f"⚠ [{input_path.name}] 第 {line_count} 行格式错误: {line[:50]}...")
                    continue

                # 构建关系对象
                relations.append({
                    "id": f"{type_prefix}-{uuid.uuid4()}",
                    "prerequisite": parts[0],
                    "target": parts[1]
                })
                success_count += 1

        # 写入标准JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(relations, f, ensure_ascii=False, indent=2)

        # 验证输出
        with open(output_path, 'r') as f:
            json.load(f)

        print(f"\n✓ [{input_path.name}] 转换成功")
        print(f"   原始行数: {line_count} | 有效记录: {success_count}")
        print(f"   生成文件: {output_path}")
        return True

    except FileNotFoundError:
        print(f"\n✗ 文件不存在: {input_path}")
        return False
    except json.JSONDecodeError:
        print(f"\n✗ JSON验证失败: {output_path}")
        return False
    except Exception as e:
        print(f"\n✗ 处理 {input_path} 时发生错误: {str(e)}")
        return False

def batch_convert():
    """批量转换所有关系文件"""
    base_dir = Path(__file__).parent

    print("="*50)
    print("开始转换关系文件".center(50))
    print("="*50)

    total_files = 0
    success_files = 0

    for rel_path in RELATION_FILES:
        input_file = base_dir / rel_path #当前目录/相对路径，拼接
        total_files += 1 #计数器

        print(f"\n▶ 正在处理: {input_file}")
        if convert_relation_file(input_file):
            success_files += 1

    print("\n" + "="*50)
    print(f"转换完成 | 成功: {success_files}/{total_files}")
    print("="*50)

if __name__ == "__main__":
    batch_convert()