import re
import json
import shutil
from pathlib import Path


def clean_hidden_chars(file_path):
    """清理结构中的隐藏字符"""
    try:
        # 读取原始内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 保留字符串内的转义字符，仅清理结构外的控制字符
        # 使用正则表达式匹配非字符串区域（基于JSON语法分析）
        pattern = r'''
            (                             # 分组1：字符串外区域
                (?:^|(?<=\}))             # 起始位置或前导}
                (?:(?!")(?:\\"|[^"])*?)   # 非字符串内容
                (?=\{|}|,|:|\[|\])        # 后视结构符号
            )
            |                             # 或
            (                             # 分组2：字符串内区域（保留）
                "(?:\\"|[^"])*?"          # 完整字符串
            )
        '''

        def replacer(match):
            # 仅处理非字符串区域
            if match.group(1):
                # 移除非法控制字符（保留必要的空格）
                return re.sub(r'[\r\n\t]+', ' ', match.group(1).strip())
            else:
                return match.group(2)

        # 执行正则替换
        cleaned = re.sub(
            pattern,
            replacer,
            content,
            flags=re.VERBOSE | re.DOTALL | re.MULTILINE
        )

        # 二次验证JSON格式
        json.loads(cleaned)

        # 写入清理后文件（备份原文件）
        backup_path = file_path.with_suffix('.json.bak')
        shutil.copy(file_path, backup_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned)

        print(f"✓ 清理完成：{file_path}")

    except Exception as e:
        print(f"✗ 清理失败：{str(e)}")
        if backup_path.exists():
            shutil.move(backup_path, file_path)
            print("已恢复备份文件")


# 执行清理
if __name__ == "__main__":
    target_files = [
        "MOOCCUBE/entities/course.json",
        # 添加其他需要清理的文件路径
    ]

    for rel_path in target_files:
        abs_path = Path(__file__).parent / rel_path
        if abs_path.exists():
            clean_hidden_chars(abs_path)
        else:
            print(f"文件不存在：{abs_path}")