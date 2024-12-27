import os
import time
import json
import mutagen # type: ignore
import subprocess
import shutil
from pathlib import Path

def format_duration(seconds):
    """将秒数转换为时分秒格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"

def get_exif_metadata(file_path):
    """使用exiftool获取文件的元数据信息"""
    exiftool = shutil.which("exiftool")
    if not exiftool:
        return None
    try:
        result = subprocess.run(
            [exiftool, "-json", "-charset", "utf8", file_path], 
            capture_output=True, 
            text=True
        ).stdout
        return json.loads(result)[0]
    except Exception as e:
        raise Exception(f"ExifTool读取失败: {str(e)}")

def get_audio_info(file_path):
    """获取音频文件的基本信息"""
    try:
        info = {
            "duration": "未知",
            "bitrate": "未知",
            "sample_rate": "未知",
            "channels": "未知",
            "format": "未知",
            "filesize": "未知",
            "encoding": "未知",
            "mime_type": "未知",
            "created_date": "未知",
            "modified_date": "未知",
            "artist": "未知",
            "title": "未知",
            "album": "未知",
            "genre": "未知",
            "year": "未知",
            "composer": "未知",
            "tags": {}
        }
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        if file_size < 1024 * 1024:
            info["filesize"] = f"{file_size / 1024:.2f} KB"
        else:
            info["filesize"] = f"{file_size / (1024 * 1024):.2f} MB"
        
        # 使用mutagen获取音频信息
        audio = mutagen.File(file_path)
        if audio is not None:
            if hasattr(audio.info, "length"):
                info["duration"] = format_duration(audio.info.length)
            if hasattr(audio.info, "bitrate"):
                info["bitrate"] = f"{int(audio.info.bitrate / 1000)} kbps"
            if hasattr(audio.info, "sample_rate"):
                info["sample_rate"] = f"{audio.info.sample_rate} Hz"
            if hasattr(audio.info, "channels"):
                info["channels"] = str(audio.info.channels)
            
            if hasattr(audio, "mime"):
                info["mime_type"] = audio.mime[0]
                info["format"] = audio.mime[0].split("/")[1].upper()
            else:
                info["format"] = Path(file_path).suffix[1:].upper()
            
            if hasattr(audio.info, "codec_description"):
                info["encoding"] = audio.info.codec_description
            elif hasattr(audio.info, "codec_name"):
                info["encoding"] = audio.info.codec_name
            
            if hasattr(audio, "tags"):
                tags = audio.tags
                if tags:
                    info["title"] = tags.get("title", ["未知"])[0] if isinstance(tags.get("title"), list) else tags.get("title", "未知")
                    info["artist"] = tags.get("artist", ["未知"])[0] if isinstance(tags.get("artist"), list) else tags.get("artist", "未知")
                    info["album"] = tags.get("album", ["未知"])[0] if isinstance(tags.get("album"), list) else tags.get("album", "未知")
                    info["genre"] = tags.get("genre", ["未知"])[0] if isinstance(tags.get("genre"), list) else tags.get("genre", "未知")
                    info["year"] = tags.get("date", ["未知"])[0] if isinstance(tags.get("date"), list) else tags.get("date", "未知")
                    info["composer"] = tags.get("composer", ["未知"])[0] if isinstance(tags.get("composer"), list) else tags.get("composer", "未知")
        
        info["created_date"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getctime(file_path)))
        info["modified_date"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(file_path)))
        
        return info
    except Exception as e:
        raise Exception(f"读取音频信息失败: {str(e)}") 