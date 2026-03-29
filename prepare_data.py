from datasets import load_dataset
import json

def main():
    print("正在加载 CommitBench 数据集...")
    dataset = load_dataset("Maxscha/commitbench", split="train")
    print(f"数据集共 {len(dataset)} 条记录")

    python_records = []
    for record in dataset:
        # 获取 diff_languages 字段（字符串，如 "py"）
        lang = record.get("diff_languages", "")
        if lang == "py":   # 只保留 Python 记录
            diff = record.get("diff", "")
            message = record.get("message", "")
            if diff and message:
                python_records.append({
                    "diff": diff,
                    "message": message
                })
                if len(python_records) % 1000 == 0:
                    print(f"已收集 {len(python_records)} 条 Python 记录...")

    print(f"共提取 {len(python_records)} 条 Python 记录")

    output_file = "retrieval_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(python_records, f, ensure_ascii=False, indent=2)
    print(f"已保存到 {output_file}")

if __name__ == "__main__":
    main()