import os
import sys
import git
from dotenv import load_dotenv
from openai import OpenAI

# 强制加载与脚本同目录下的 .env 文件
from pathlib import Path
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("SILICONFLOW_API_KEY")
if not API_KEY:
    raise ValueError("未找到 SILICONFLOW_API_KEY，请在 .env 文件中设置该变量")

BASE_URL = "https://api.siliconflow.cn/v1"
MODEL = "Pro/zai-org/GLM-5"

def get_git_diff(repo_path="."):
    """获取当前工作区未暂存的变更"""
    try:
        repo = git.Repo(repo_path)
        diff = repo.git.diff()
        return diff
    except Exception as e:
        print(f"读取 Git 仓库失败：{e}")
        return None

def generate_commit_message(diff_text, retry=3):
    """调用 API 生成提交信息，支持重试，超时 120 秒"""
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=120)
    for attempt in range(1, retry + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的代码助手，擅长根据代码变更生成规范的 Git 提交信息（遵循 Conventional Commits 格式）。"},
                    {"role": "user", "content": f"根据以下代码变更，生成一条规范的 Git 提交信息：\n\n{diff_text}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"API 调用失败 (尝试 {attempt}/{retry}): {e}")
            if attempt == retry:
                return None
    return None

def main():
    repo_path = input("请输入 Git 仓库路径（直接回车表示当前目录）: ").strip()
    if not repo_path:
        repo_path = "."

    diff = get_git_diff(repo_path)
    if not diff:
        print("没有未提交的变更，或无法读取变更。")
        sys.exit(0)

    print("正在分析代码变更...")
    commit_msg = generate_commit_message(diff)
    if commit_msg:
        print("\n生成的提交信息：")
        print(commit_msg)
    else:
        print("生成失败。")

if __name__ == "__main__":
    main()
