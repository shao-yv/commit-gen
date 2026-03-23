import os
import sys
import git
import argparse
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

def get_git_diff(repo_path=".", staged=False):
    """获取当前工作区或暂存区的变更"""
    try:
        repo = git.Repo(repo_path)
        if staged:
            diff = repo.git.diff('--cached')
        else:
            diff = repo.git.diff()
        return diff
    except Exception as e:
        print(f"读取 Git 仓库失败：{e}")
        return None

def generate_commit_message(diff_text, retry=3):
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
                # 降级：返回一个通用提交信息
                print("使用降级方案生成提交信息。")
                return "chore: 更新代码（AI 服务暂时不可用，请手动补充说明）"
    return None  # 理论上不会执行到这

def main():
    parser = argparse.ArgumentParser(description='生成规范的Git提交信息')
    parser.add_argument('-p', '--path', default='.', help='Git仓库路径（默认为当前目录）')
    parser.add_argument('-s', '--stage', action='store_true', help='显示暂存区变更（git diff --cached）')
    args = parser.parse_args()

    diff = get_git_diff(repo_path=args.path, staged=args.stage)
    if not diff:
        print("没有未提交的变更，或无法读取变更。")
        sys.exit(0)

    print("正在分析代码变更...")
    commit_msg = generate_commit_message(diff)
    if commit_msg:
        print("\n生成的提交信息：")
        print(commit_msg)
        if "AI 服务暂时不可用" in commit_msg:
            print("（注意：由于 AI 服务暂时不可用，以上为降级方案生成的通用提交信息。）")
    else:
        print("生成失败。")

if __name__ == "__main__":
    main()
