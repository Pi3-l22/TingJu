import re
from pathlib import Path

import pymupdf
from utils.logger import logger

FILE_TYPES = ['.pdf', '.xps', '.epub', '.mobi', '.fb2', '.cbz', '.svg', '.txt', '.docx', '.xlsx', '.pptx']

def list_file_types() -> list:
    return FILE_TYPES

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
        
        # 如果有连续的多个空格，则替换成单个空格
        text = re.sub(r"\s+", " ", text)
        
        logger.info(f"{file.name} 提取文字成功")
        return text
    except Exception as e:
        logger.error(f"处理 {file_path} 文件时出错: {str(e)}")
        return ""
    finally:
        try:
            doc.close()
        except:
            pass