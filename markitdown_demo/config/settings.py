import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础配置
BASE_URL = os.getenv("BASE_URL")
FILES_DIR = Path("files")
FILES_DIR.mkdir(exist_ok=True)

# OpenAI配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

# Azure OpenAI配置
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# 使用限制配置
VALID_CONVERT_CNT = int(os.getenv("VALID_CONVERT_CNT", "10"))
VALID_CHAT_CNT = int(os.getenv("VALID_CHAT_CNT", "10"))

# 支持的文件格式
SUPPORTED_EXTENSIONS = (
    '.pptx', '.ppt', '.docx', '.doc', '.pdf', 
    '.jpg', '.jpeg', '.png', '.txt', '.xml', 
    '.xlsx', '.mp3', '.wav'
)

# 模型配置
MODEL_OPTIONS = {
    "GPT-4-Mini": "gpt-4o-mini",
    "GPT-3.5-Turbo": "gpt-3.5-turbo-0125"
}

# 应用配置
MAX_FILES = 10
MAX_PREVIEW_CHARS = 1500
FILE_CLEANUP_TIME = 1800  # 30分钟 