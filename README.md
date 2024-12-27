# MarkitDown Converter - 智能文档转换助手 🚀

 [MarkitDown](https://github.com/microsoft/markitdown/)是微软开源的一个强大的文档转换工具，能够将各种格式的文档智能转换为 Markdown 格式，在基础上实现了可视化预览处理，并支持与 AI 助手进行实时对话，帮助您更好地理解和编辑文档内容。

## ✨ 核心功能

- 🔄 多格式文档转换
  - 支持 PDF、Word、Excel、图片等多种文档格式
  - 支持网页 URL 直接转换
  - 智能保留文档原有格式和样式

- 🤖 AI 智能助手
  - 实时对话功能，解答文档相关问题
  - 智能内容优化和建议
  - 支持多种 AI 模型选择

- 👀 实时预览
  - 双栏设计，源文档和转换结果实时对比
  - Markdown 实时渲染预览
  - 支持多文档同时处理

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip 包管理器

### 安装步骤

1. 克隆项目到本地：
```bash
git clone [项目地址]
cd markitdown-demo
```



3. 配置环境变量：
创建 `.env` 文件并配置以下内容：
```
OPENAI_API_KEY=你的OpenAI API密钥
OPENAI_API_BASE=你的API基础URL（可选）
```

4. 启动应用：
```bash
# 进入shell
poetry shell

# 安装依赖：
pip3 install -r requirements.txt

# 启动应用
streamlit run run.py
```

启动后访问 `http://localhost:8501` 即可使用。

## 🎯 使用限制

- 单次最多支持上传 10 个文件
- 支持格式：PDF、Word、Excel、图片等
- 需要有效的 OpenAI API 密钥
- 自定义....

## 💖 支持项目

如果您觉得这个项目对您有帮助，欢迎打赏支持！
微信：
![微信打赏码](https://minioapi.nonezero.top/dz-minio-os/wx%E6%94%B6%E6%AC%BE.jpg)

支付宝：
![支付宝打赏码](https://minioapi.nonezero.top/dz-minio-os/zfb%E6%94%B6%E6%AC%BE.jpg)

## 📝 许可证

[MIT License](LICENSE)
