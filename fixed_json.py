# MOOC_Recommender/fixed_json.py
import os
import json
import shutil
from pathlib import Path

TARGET_FILES = [
    #"MOOCUBE/entities/user.json",
    #"MOOCUBE/entities/video.json",
    #"MOOCUBE/entities/concept.json",
    #"MOOCUBE/entities/course.json",
    "MOOCCUBE/relations/prerequisite-dependency.json",
    "MOOCCUBE/relations/user-course.json",
    "MOOCCUBE/relations/course-concept.json"
]


def repair_json_file(file_path):
    backup_path = file_path + ".bak"  # 提前定义备份路径

    try:
        # 创建备份（无论是否已存在）
        shutil.copyfile(file_path, backup_path)

        # 读取并验证原始数据
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = []
            for i, line in enumerate(f, 1):
                stripped = line.strip()
                if not stripped:
                    continue

                # 预验证每行JSON
                try:
                    json.loads(stripped)
                    lines.append(stripped)
                except json.JSONDecodeError as e:
                    raise ValueError(f"第 {i} 行不是有效的JSON: {str(e)}")

        # 生成修复后的内容
        repaired = "[\n" + ",\n".join(lines) + "\n]"

        # 二次验证整体结构
        json.loads(repaired)

        # 写入修复文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(repaired)

        print(f"✓ 成功修复 {file_path}")
        return True

    except Exception as e:
        print(f"✗ 修复失败 {file_path}\n错误原因: {str(e)}")
        # 恢复备份
        if os.path.exists(backup_path):
            shutil.move(backup_path, file_path)
            print(f"已恢复原始文件 {file_path}")
        return False


def main():
    project_root = Path(__file__).parent

    for rel_path in TARGET_FILES:
        abs_path = project_root / rel_path

        if not abs_path.exists():
            print(f"⚠ 文件不存在：{abs_path}，跳过处理")
            continue

        print(f"\n▶ 开始处理 {abs_path}")
        success = repair_json_file(str(abs_path))
        if success:
            print(f"√ 验证通过：{json.load(open(abs_path))[:1]}...（已截断预览）")


if __name__ == "__main__":
    main()