from datasets import load_dataset
import json

def main():
    # 1. 加载数据集（只加载训练集，因为测试集结构类似）
    print("正在加载 CommitBench 数据集（这可能需要几分钟，首次会下载约 1.6GB）...")
    dataset = load_dataset("Maxscha/commitbench", split="train")
    print(f"数据集共 {len(dataset)} 条记录")

    # 2. 筛选 Python 语言，并提取 diff 和 message
    python_records = []
    for record in dataset:
        # 根据数据集结构，语言字段可能是 "language" 或 "lang"，先尝试常用字段
        lang = record.get("language", record.get("lang", ""))
        if lang == "Python":
            diff = record.get("diff", "")
            message = record.get("message", "")
            if diff and message:
                python_records.append({
                    "diff": diff,
                    "message": message
                })
                # 可选：打印进度（每1000条打印一次）
                if len(python_records) % 1000 == 0:
                    print(f"已收集 {len(python_records)} 条 Python 记录...")

    print(f"共提取 {len(python_records)} 条 Python 记录")

    # 3. 保存到 retrieval_data.json
    output_file = "retrieval_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(python_records, f, ensure_ascii=False, indent=2)
    print(f"已保存到 {output_file}")

if __name__ == "__main__":
    main()