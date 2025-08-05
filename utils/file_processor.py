import re
from pathlib import Path

import pymupdf
from utils.logger import logger
from utils.text_processor import normalize_text

FILE_TYPES = ['.pdf', '.txt', '.docx', '.xlsx', '.pptx', '.svg', '.epub', '.mobi', '.xps', '.fb2', '.cbz']

def extract_text_from_file(file_path: str) -> str:
    # 先检查文件类型是否正确，文件是否存在
    file = Path(file_path)
    if file.suffix not in FILE_TYPES:
        logger.error(f"文件类型不支持: {file_path}")
        return ""
    if not file.exists():
        logger.error(f"文件不存在: {file_path}")
        return ""
    
    # 打开文件并确保正确关闭
    try:
        doc = pymupdf.open(file_path)
        logger.info(f"{file.name} 打开成功，共 {len(doc)} 页")
        
        # 遍历所有页
        text = ""
        for page in doc.pages():
            page_str = page.get_text()
            # 去除 \n 合并成一整段
            page_str = page_str.replace("\n", " ")
            text += page_str
            logger.debug(f"{file.name} 页 {page.number} 提取文字成功")
        
        # 规范化文本
        text = normalize_text(text)
        
        logger.info(f"{file.name} 提取文字完成")
        return text
    except Exception as e:
        logger.error(f"{file_path} 提取文字出错: {str(e)}")
        return ""
    finally:
        try:
            doc.close()
        except:
            pass