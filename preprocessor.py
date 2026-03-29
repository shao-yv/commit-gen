import chromadb
import requests
from config import API_KEY, BASE_URL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 初始化 ChromaDB 客户端（持久化）
client = chromadb.PersistentClient(path="./chroma_db")
collection_name = "commit_messages"
# 注意：获取集合时不需要指定 embedding_function，因为检索时我们会手动生成查询向量
collection = client.get_collection(collection_name)

# 自定义嵌入函数（用于将查询 diff 转成向量）
class SiliconFlowEmbeddingFunction:
    def __init__(self, api_key, model_name, base_url):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url

    def __call__(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "input": texts
        }
        response = requests.post(url, headers=headers, json=payload, timeout=60, verify=False)
        if response.status_code != 200:
            raise Exception(f"嵌入 API 失败: {response.text}")
        data = response.json()
        return [item["embedding"] for item in data["data"]]

# 创建嵌入函数实例（使用与构建时相同的模型）
ef = SiliconFlowEmbeddingFunction(API_KEY, "Qwen/Qwen3-Embedding-8B", BASE_URL)

def retrieve_examples(diff, k=3):
    """检索与 diff 最相似的 k 条历史提交信息"""
    try:
        # 将 diff 转为向量
        query_embedding = ef([diff])[0]
        # 查询
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas"]
        )
        examples = []
        for i, doc in enumerate(results['documents'][0]):
            msg = results['metadatas'][0][i]['message']
            examples.append(f"示例 {i+1}:\ndiff:\n{doc}\n提交信息:\n{msg}\n")
        return "\n".join(examples)
    except Exception as e:
        print(f"检索示例失败: {e}")
        return ""

def analyze(diff):
    """预处理：返回检索到的示例（若有）"""
    examples = retrieve_examples(diff)
    if examples:
        return {"examples": examples}
    return {}