import os
import uuid
import time
import fitz # type: ignore
import shutil
import tempfile
from pathlib import Path
from PIL import Image
import pandas as pd
import xml.dom.minidom
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from markitdown_demo.config.settings import FILES_DIR, BASE_URL, FILE_CLEANUP_TIME

def save_uploaded_file(uploaded_file):
    """保存上传的文件并返回URL"""
    file_extension = Path(uploaded_file.name).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = FILES_DIR / unique_filename
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    file_url = f"{BASE_URL}/files/{unique_filename}"
    return str(file_path), file_url

def cleanup_old_files():
    """清理超过30分钟的临时文件"""
    current_time = time.time()
    for file_path in FILES_DIR.glob("*"):
        if current_time - file_path.stat().st_mtime > FILE_CLEANUP_TIME:
            try:
                file_path.unlink()
            except Exception:
                pass

def display_pdf(pdf_path):
    """显示PDF预览"""
    try:
        doc = fitz.open(pdf_path)
        if len(doc) > 0:
            page = doc[0]
            zoom = 1.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img_data = pix.samples
            img = Image.frombytes("RGB", [pix.width, pix.height], img_data)
            return img, len(doc)
        doc.close()
        return None, 0
    except Exception as e:
        raise Exception(f"PDF预览失败: {str(e)}")

def get_webpage_info(url):
    """获取网页的基本信息"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        if response.encoding.lower() == 'iso-8859-1':
            content_type = response.headers.get('content-type', '').lower()
            if 'charset=' in content_type:
                encoding = content_type.split('charset=')[-1]
                response.encoding = encoding
            else:
                response.encoding = response.apparent_encoding
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string.strip() if soup.title else "无标题"
        
        description = ""
        meta_description = soup.find("meta", attrs={"name": "description"})
        if meta_description:
            description = meta_description.get("content", "").strip()
        else:
            og_description = soup.find("meta", attrs={"property": "og:description"})
            if og_description:
                description = og_description.get("content", "").strip()
            else:
                first_p = soup.find('p')
                if first_p:
                    description = first_p.get_text().strip()[:200] + "..."
        
        domain = urlparse(url).netloc
        
        return {
            "title": ' '.join(title.split()) if title else "无标题",
            "description": ' '.join(description.split()) if description else "无描述",
            "domain": domain,
            "status_code": response.status_code,
            "content_type": response.headers.get('content-type', ''),
        }
    except Exception as e:
        raise Exception(f"获取网页信息失败: {str(e)}")

def handle_xml_file(file_content):
    """处理XML文件"""
    try:
        dom = xml.dom.minidom.parseString(file_content)
        return dom.toprettyxml()
    except Exception as e:
        raise Exception(f"XML格式错误: {str(e)}")

def handle_excel_file(file):
    """处理Excel文件"""
    try:
        return pd.read_excel(file)
    except Exception as e:
        raise Exception(f"Excel读取错误: {str(e)}")

def handle_text_file(file_content):
    """处理文本文件"""
    try:
        return file_content.decode('utf-8')
    except Exception as e:
        raise Exception(f"文本文件读取错误: {str(e)}")

def get_file_path(file_name):
    """根据文件名获取文件路径"""
    return FILES_DIR / file_name 