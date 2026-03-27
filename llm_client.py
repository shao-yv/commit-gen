from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL, TIMEOUT, RETRY_TIMES

def generate(prompt):
    """调用 LLM API 生成文本，失败时返回降级信息"""
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=TIMEOUT)
    for attempt in range(1, RETRY_TIMES + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"API 调用失败 (尝试 {attempt}/{RETRY_TIMES}): {e}")
            if attempt == RETRY_TIMES:
                print("使用降级方案生成提交信息。")
                return "chore: 更新代码（AI 服务暂时不可用，请手动补充说明）"
    return None