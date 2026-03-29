import json
import chromadb
from chromadb.utils import embedding_functions
import requests
import time
import os
import argparse
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
API_KEY = os.getenv("SILICONFLOW_API_KEY")
BASE_URL = "https://api.siliconflow.cn/v1"
EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-8B"   # 可换成其他模型
BATCH_SIZE = 32            # API 单次最大条数
TIMEOUT = 120              # 请求超时秒数
MAX_RETRIES = 5            # 重试次数
RETRY_DELAY = 2            # 初始重试延迟（秒）
SLEEP_BETWEEN_BATCHES = 0.5  # 批次间休眠

# 自定义嵌入函数
class SiliconFlowEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, api_key, model_name, base_url):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url

    def __call__(self, input):
        if isinstance(input, str):
            texts = [input]
        else:
            texts = input
        # 分批处理（防止超长列表）
        all_embeddings = []
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i:i+BATCH_SIZE]
            batch_emb = self._request_embeddings(batch)
            all_embeddings.extend(batch_emb)
        return all_embeddings

    def _request_embeddings(self, texts):
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": EMBEDDING_MODEL,
            "input": texts
        }
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    embeddings = [item["embedding"] for item in data["data"]]
                    return embeddings
                else:
                    print(f"嵌入 API 返回错误 (尝试 {attempt}/{MAX_RETRIES}): {response.status_code} - {response.text}")
            except Exception as e:
                print(f"嵌入 API 请求异常 (尝试 {attempt}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES:
                wait = RETRY_DELAY * (2 ** (attempt - 1))
                print(f"等待 {wait} 秒后重试...")
                time.sleep(wait)
        raise Exception(f"嵌入 API 调用失败，已达最大重试次数")

def get_progress(progress_file):
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            return int(f.read().strip())
    return 0

def save_progress(progress_file, idx):
    with open(progress_file, "w") as f:
        f.write(str(idx))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="测试模式（只取前N条）")
    parser.add_argument("--size", type=int, default=5000, help="测试模式下使用的记录数")
    args = parser.parse_args()

    # 加载数据
    print("加载 retrieval_data.json ...")
    with open("retrieval_data.json", "r", encoding="utf-8") as f:
        all_records = json.load(f)
    if args.test:
        all_records = all_records[:args.size]
        print(f"测试模式：使用前 {args.size} 条记录")
    else:
        print(f"共 {len(all_records)} 条记录")

    # 创建嵌入函数实例（供创建和获取集合时使用）
    ef = SiliconFlowEmbeddingFunction(API_KEY, EMBEDDING_MODEL, BASE_URL)

    # 初始化 ChromaDB
    client = chromadb.PersistentClient(path="./chroma_db")
    collection_name = "commit_messages"
    try:
        # 获取已有集合时，明确指定 embedding_function
        collection = client.get_collection(collection_name, embedding_function=ef)
        existing = collection.count()
        print(f"获取已有集合 {collection_name}，已有 {existing} 条记录")
    except:
        # 集合不存在，创建
        collection = client.create_collection(
            name=collection_name,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"}
        )
        existing = 0
        print(f"创建集合 {collection_name}")

    # 断点续传
    progress_file = ".build_progress"
    start_idx = get_progress(progress_file)
    if start_idx < existing:
        print(f"进度文件记录 {start_idx}，但集合中已有 {existing}，将从 {existing} 开始")
        start_idx = existing
    else:
        print(f"从进度文件记录 {start_idx} 开始")

    total = len(all_records)
    failed_batches = []
    for start in range(start_idx, total, BATCH_SIZE):
        end = min(start + BATCH_SIZE, total)
        batch = all_records[start:end]
        ids = [f"{start+i}" for i in range(len(batch))]
        documents = [record["diff"] for record in batch]
        metadatas = [{"message": record["message"]} for record in batch]

        try:
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            print(f"已插入 {end} / {total} 条")
            save_progress(progress_file, end)
            time.sleep(SLEEP_BETWEEN_BATCHES)
        except Exception as e:
            print(f"插入批次 {start}-{end} 失败: {e}")
            failed_batches.append((start, end))
            # 继续下一批次

    if failed_batches:
        print(f"以下批次失败: {failed_batches}")
    else:
        print("向量库构建完成！")
        if os.path.exists(progress_file):
            os.remove(progress_file)

if __name__ == "__main__":
    main()