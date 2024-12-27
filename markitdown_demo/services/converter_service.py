from pathlib import Path
import tempfile
from markitdown import MarkItDown
from markitdown_demo.services.openai_service import client, translate_to_chinese, transcribe_audio
from markitdown_demo.utils.user_tracker import UserTracker

# 初始化用户追踪器
user_tracker = UserTracker()

class ConverterService:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        self.md = MarkItDown(llm_client=client, llm_model=model)
    
    def convert_url(self, url, ip='unknown'):
        """转换URL为Markdown"""
        try:
            result = self.md.convert(url)
            return result.text_content
        except Exception as e:
            raise Exception(f"URL转换失败: {str(e)}")
    
    def convert_file(self, file_path, file_extension):
        """转换文件为Markdown"""
        try:
            if file_extension.lower() in ['.mp3', '.wav']:
                # 音频文件使用Whisper转录
                transcription = transcribe_audio(file_path)
                markdown_content = f"""# 音频转录结果

## 文件信息
- 文件名：{Path(file_path).name}
- 格式：{file_extension[1:].upper()}

## 转录内容
{transcription}
"""
                return markdown_content
            
            # 其他文件用MarkItDown转换
            result = self.md.convert(file_path)
            
            # 如果是图片文件，将结果翻译成中文
            if file_extension.lower() in ['.jpg', '.jpeg', '.png']:
                result.text_content = translate_to_chinese(result.text_content)
            
            return result.text_content
        except Exception as e:
            raise Exception(f"文件转换失败: {str(e)}")
    
    def convert_files(self, files, ip='unknown'):
        """批量转换文件"""
        results = {}
        try:
            for file in files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.name).suffix) as tmp_file:
                    tmp_file.write(file.getvalue())
                    try:
                        result = self.convert_file(tmp_file.name, Path(file.name).suffix)
                        results[file.name] = result
                    except Exception as e:
                        results[file.name] = str(e)
                    finally:
                        Path(tmp_file.name).unlink(missing_ok=True)
            return results
        except Exception as e:
            raise Exception(f"批量转换失败: {str(e)}") 