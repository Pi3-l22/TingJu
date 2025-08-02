import asyncio
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils.file_processor import extract_text_from_file
from utils.text_processor import init_nltk, get_sentences
from utils.text_translator import get_text_translated
from utils.audio_generator import generate_audio_sync
from utils.logger import logger

app = FastAPI()

# 挂载静态文件目录
app.mount("/audios", StaticFiles(directory="audios"), name="audios")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# 配置模板
templates = Jinja2Templates(directory="templates")

# 初始化NLTK
init_nltk()

# 用于存储临时文件路径的全局变量
TEMP_FILE_PATH: Optional[Path] = None

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    根路由，返回工具介绍和文件上传页面
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    """
    处理文件上传，提取文本内容
    """
    # 创建临时文件保存上传的文件
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    # 生成唯一的文件名
    filename = file.filename or "unknown"
    file_extension = Path(filename).suffix
    temp_file_name = f"{uuid.uuid4()}{file_extension}"
    temp_file_path = temp_dir / temp_file_name
    
    # 保存上传的文件
    with open(temp_file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # 提取文本
    try:
        extracted_text = extract_text_from_file(str(temp_file_path))
        if not extracted_text:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": "无法从文件中提取文本，请确保文件格式正确且包含文本内容。"
            })
        
        # 保存临时文件路径到全局变量
        global TEMP_FILE_PATH
        TEMP_FILE_PATH = temp_file_path
        
        # 跳转到文本确认页面
        return templates.TemplateResponse("text_confirm.html", {
            "request": request,
            "text": extracted_text
        })
    except Exception as e:
        logger.error(f"处理文件时出错: {str(e)}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"处理文件时出错: {str(e)}"
        })

@app.post("/process_text")
async def process_text(request: Request, text: str = Form(...)):
    """
    处理用户确认的文本，进行分句、翻译和音频生成
    """
    try:
        # 对文本进行分句
        sentences = get_sentences(text)
        
        if not sentences:
            return templates.TemplateResponse("text_confirm.html", {
                "request": request,
                "text": text,
                "error": "未能从文本中分割出句子，请检查文本内容。"
            })
        
        # 生成标题（用于音频文件夹名称）
        title = str(uuid.uuid4())[:8]
        
        # 翻译句子
        translated_sentences = get_text_translated(sentences)
        
        # 生成音频
        voice_name = "en-US-ChristopherNeural"
        generate_audio_sync(sentences, voice_name, title)
        
        # 构建结果列表
        results = []
        audio_dir = Path("audios") / title
        
        for i, (sentence, translation) in enumerate(zip(sentences, translated_sentences)):
            # 构建音频文件路径
            # 注意：这里需要与audio_generator中的文件命名方式保持一致
            import hashlib
            stripped_text = sentence.strip()
            text_hash = hashlib.md5(stripped_text.encode('utf-8')).hexdigest()
            audio_filename = f"{i+1}_{text_hash}.mp3"
            audio_path = f"audios/{title}/{audio_filename}"
            
            results.append({
                "sentence": sentence,
                "translation": translation,
                "audio_path": audio_path
            })
        
        # 清理临时文件
        global TEMP_FILE_PATH
        if TEMP_FILE_PATH and TEMP_FILE_PATH.exists():
            TEMP_FILE_PATH.unlink()
            TEMP_FILE_PATH = None
        
        # 返回结果页面
        return templates.TemplateResponse("results.html", {
            "request": request,
            "results": results
        })
        
    except Exception as e:
        logger.error(f"处理文本时出错: {str(e)}")
        return templates.TemplateResponse("text_confirm.html", {
            "request": request,
            "text": text,
            "error": f"处理文本时出错: {str(e)}"
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=51122)