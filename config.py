import os
from dotenv import load_dotenv
from pathlib import Path

# 加载 .env 文件（与当前文件同目录）
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("SILICONFLOW_API_KEY")
if not API_KEY:
    raise ValueError("未找到 SILICONFLOW_API_KEY，请在 .env 文件中设置该变量")

BASE_URL = "https://api.siliconflow.cn/v1"
MODEL = "Pro/zai-org/GLM-5"        # 可根据需要修改
TIMEOUT = 120                       # 超时秒数
RETRY_TIMES = 3                     # 重试次数