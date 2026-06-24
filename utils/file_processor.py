import re
from pathlib import Path

import pymupdf
from utils.logger import logger
from utils.text_processor import normalize_text

FILE_TYPES = ['.pdf', '.txt', '.docx', '.xlsx', '.pptx', '.svg', '.epub', '.mobi', '.xps', '.fb2', '.cbz', '.md']

def extract_text_from_file(file_path: str) -> str:
    """
    提取文件中的文字

    Args:
        file_path (str): 需要提取的文件路径

    Returns:
        str: 提取到的文字信息
    """
    # 先检查文件类型是否正确，文件是否存在
    file = Path(file_path)
    if file.suffix not in FILE_TYPES:
        logger.error(f"文件类型不支持: {file_path}")
        return ""
    if not file.exists():
        logger.error(f"文件不存在: {file_path}")
        return ""
    
    # 处理 Markdown 文件
    if file.suffix.lower() == '.md':
        return extract_text_from_markdown(file_path)
    
    # 处理其他文件类型（使用 PyMuPDF）
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
        
        # 处理多余的空格（包括添加空格后产生的多个连续空格）
        text = re.sub(r'\s+', ' ', text)
        
        # 去除前后空白符
        text = text.strip()
        
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


def extract_text_from_markdown(file_path: str) -> str:
    """
    从 Markdown 文件中提取纯文本内容，专为英语学习优化
    - 移除代码块
    - 移除 Markdown 格式标记
    - 保留纯文本内容

    Args:
        file_path (str): Markdown 文件路径

    Returns:
        str: 提取到的纯文本内容
    """
    try:
        file = Path(file_path)
        logger.info(f"开始处理 Markdown 文件: {file.name}")
        
        # 读取 Markdown 文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 移除代码块（包括行内代码和代码块）
        # 移除三个反引号的代码块
        markdown_content = re.sub(r'```[\s\S]*?```', '', markdown_content)
        # 移除单个反引号的行内代码
        markdown_content = re.sub(r'`[^`]*`', '', markdown_content)
        
        # 移除 Markdown 格式标记
        # 移除标题标记
        markdown_content = re.sub(r'^#{1,6}\s+', '', markdown_content, flags=re.MULTILINE)
        # 移除粗体和斜体标记
        markdown_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', markdown_content)  # **bold**
        markdown_content = re.sub(r'\*([^*]+)\*', r'\1', markdown_content)      # *italic*
        markdown_content = re.sub(r'__([^_]+)__', r'\1', markdown_content)      # __bold__
        markdown_content = re.sub(r'_([^_]+)_', r'\1', markdown_content)        # _italic_
        # 移除链接，保留链接文本
        markdown_content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', markdown_content)
        # 移除图片
        markdown_content = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', markdown_content)
        # 移除列表标记
        markdown_content = re.sub(r'^[\s]*[-*+]\s+', '', markdown_content, flags=re.MULTILINE)
        markdown_content = re.sub(r'^\s*\d+\.\s+', '', markdown_content, flags=re.MULTILINE)
        # 移除引用标记
        markdown_content = re.sub(r'^>\s*', '', markdown_content, flags=re.MULTILINE)
        # 移除水平分割线
        markdown_content = re.sub(r'^[-*_]{3,}$', '', markdown_content, flags=re.MULTILINE)
        
        # 处理多余的空格和换行
        text = re.sub(r'\n+', ' ', markdown_content)  # 将换行转为空格
        text = re.sub(r'\s+', ' ', text)              # 合并多个空格
        text = text.strip()
        
        logger.info(f"Markdown 文件 {file.name} 处理完成，提取文本长度: {len(text)}")
        return text
        
    except Exception as e:
        logger.error(f"处理 Markdown 文件 {file_path} 时出错: {str(e)}")
        return ""