# convert_json.py
import json

input_file = "users.json"
output_file = "users_fixed.json"

with open(input_file, "r", encoding="utf-8") as f_in:
    # 读取所有行并解析为字典
    data = [json.loads(line) for line in f_in]

with open(output_file, "w", encoding="utf-8") as f_out:
    json.dump(data, f_out, ensure_ascii=False, indent=2)