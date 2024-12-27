from openai import OpenAI, AzureOpenAI
from ..config.settings import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_ENDPOINT
)

# 初始化OpenAI客户端
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL
)

# 初始化Azure OpenAI客户端
azure_client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

def translate_to_chinese(text, model="gpt-4o-mini"):
    """将英文文本转换为中文"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个专业的翻译助手，请将以下英文内容翻译成地道的中文，保持专业性和准确性。"},
                {"role": "user", "content": f"请将以下内容翻译成中文：\n{text}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"翻��失败: {str(e)}")

def transcribe_audio(file_path, model="whisper-1"):
    """使用Azure OpenAI的Whisper模型转录音频文件"""
    try:
        with open(file_path, "rb") as audio_file:
            response = azure_client.audio.transcriptions.create(
                file=audio_file,
                model=model,
                response_format="text",
                prompt="请将以下音频内容转换为中文或者英文,如果为汉语则简体中文,如果非汉语则转换成为英文,并保持原文的格式和结构。"
            )
            return response
    except Exception as e:
        raise Exception(f"音频转录失败: {str(e)}")

def chat_with_content(content, user_input, model="gpt-4o-mini"):
    """与文档内容进行对话"""
    try:
        system_prompt = f"""你是一个专业的文档助手，你需要基于以下文档内容回答用户的问题。
请注意：
1. 只使用提供的文档内容来回答问题
2. 如果问题超出文档范围，请明确告知
3. 保持回答简洁专业
4. 可以适当引用文档中的原文

文档内容：
{content}
"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            stream=True
        )
        return response
    except Exception as e:
        raise Exception(f"对话失败: {str(e)}") 