import uuid
import atexit
import shutil
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime as dt

from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils.file_processor import extract_text_from_file
from utils.text_processor import init_nltk, get_sentences
from utils.text_translator import get_text_translated
from utils.audio_generator import generate_audio, list_voices, AUDIO_DIR
from utils.logger import logger

# 存储临时文件路径的全局变量
TEMP_FILE_PATH: Optional[Path] = None

# 临时目录 导出目录
TEMP_DIR = "temp"
EXPORT_DIR = "exports"

# 存储当前的UUID
CURRENT_UUID: str = ""

app = FastAPI()

# 创建音频目录
Path(AUDIO_DIR).mkdir(exist_ok=True)
# 创建临时目录
Path(TEMP_DIR).mkdir(exist_ok=True)

# 挂载静态文件目录
app.mount(f"/{AUDIO_DIR}", StaticFiles(directory=AUDIO_DIR), name=AUDIO_DIR)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# 配置模板
templates = Jinja2Templates(directory="templates")

def cleanup_temp_files():
    """清理临时文件和音频文件"""
    try:
        # 清理temp目录
        temp_dir = Path(TEMP_DIR)
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            temp_dir.mkdir(exist_ok=True)
            logger.info("temp 文件夹已清理")
        
        # 清理audios目录
        audio_dir = Path(AUDIO_DIR)
        if audio_dir.exists():
            shutil.rmtree(audio_dir)
            audio_dir.mkdir(exist_ok=True)
            logger.info("audios 文件夹已清理")
    except Exception as e:
        logger.error(f"清理临时文件时出错: {e}")

# 注册程序退出时的清理函数
atexit.register(cleanup_temp_files)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """根路由，返回工具介绍和文件上传页面"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/manual", response_class=HTMLResponse)
async def manual_input(request: Request):
    """手动填写文本内容"""
    return templates.TemplateResponse("text.html", {
        "request": request,
        "text": ""  # 空文本，让用户自行填写
    })

@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    """处理文件上传，提取文本内容"""
    # 创建临时文件保存上传的文件
    temp_dir = Path(TEMP_DIR)
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
        return templates.TemplateResponse("text.html", {
            "request": request,
            "text": extracted_text
        })
    except Exception as e:
        logger.error(f"处理文件 {file.filename} 时出错: {str(e)}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"处理文件时出错: {str(e)}"
        })

@app.post("/generate")
async def generate(request: Request, text: str = Form(...), voice: str = Form(...)):
    """处理用户确认的文本，进行分句、翻译和音频生成"""
    try:
        # 对文本进行分句
        sentences = get_sentences(text)
        
        if not sentences:
            return templates.TemplateResponse("text.html", {
                "request": request,
                "text": text,
                "error": "未能从文本中分割出句子，请检查文本内容。"
            })
        
        # 生成标题（用于音频文件夹名称）
        title = str(uuid.uuid4())[:8]
        
        # 翻译句子
        translated_sentences = get_text_translated(sentences)
        
        # 生成音频
        voice_name = voice if voice else "en-US-ChristopherNeural"
        audio_dir, audio_filenames = await generate_audio(sentences, voice_name, title)
        
        # 构建结果列表
        results = []
        for i, (sentence, translation, audio_filename) in enumerate(zip(sentences, translated_sentences, audio_filenames)):
            audio_path = Path(audio_dir) / audio_filename
            results.append({
                "sentence": sentence,
                "translation": translation,
                "audio_path": str(audio_path).replace("\\", "/")  # 确保路径分隔符统一
            })
        
        # 清理临时文件
        global TEMP_FILE_PATH
        if TEMP_FILE_PATH and TEMP_FILE_PATH.exists():
            TEMP_FILE_PATH.unlink()
            TEMP_FILE_PATH = None
        
        # 保存html文件 用于后续导出
        save_html(title, {"results": results})
        
        # 保存当前的UUID标题
        global CURRENT_UUID
        CURRENT_UUID = title
        
        # 返回结果页面
        return templates.TemplateResponse("results.html", {
            "request": request,
            "results": results,
        })
        
    except Exception as e:
        logger.error(f"处理文本时出错: {str(e)}")
        return templates.TemplateResponse("text.html", {
            "request": request,
            "text": text,
            "error": f"处理文本时出错: {str(e)}"
        })

@app.get("/voices")
async def get_voices():
    """获取可用的音色列表"""
    try:
        voices = await list_voices()
        return {"voices": voices}
    except Exception as e:
        logger.error(f"获取音色列表时出错: {str(e)}")
        return {"error": f"获取音色列表时出错: {str(e)}"}

@app.get("/export")
async def export_content():
    """导出当前结果页面和音频文件"""
    try:
        # 创建导出目录
        export_dir = Path(EXPORT_DIR)
        export_dir.mkdir(exist_ok=True)
        
        # 创建一个文件夹存放本次导出的文件
        export_folder = export_dir / f"TingJu_{dt.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        export_folder.mkdir(exist_ok=True)
        index_html= Path(export_folder, "index.html")
        css_dir = Path(export_folder, "css")
        css_dir.mkdir(exist_ok=True)
        js_dir = Path(export_folder, "js")
        js_dir.mkdir(exist_ok=True)
        img_dir = Path(export_folder, "img")
        img_dir.mkdir(exist_ok=True)
        audios_dir = Path(export_folder, AUDIO_DIR)
        audios_dir.mkdir(exist_ok=True)
        
        # 将html css js favicon.png audios 复制到 export_folder 下
        shutil.copy(Path(TEMP_DIR, f"{CURRENT_UUID}.html"), index_html)
        shutil.copy(Path("static", "css", "common.css"), css_dir)
        shutil.copy(Path("static", "css", "results.css"), css_dir)
        shutil.copy(Path("static", "css", "theme.css"), css_dir)
        shutil.copy(Path("static", "js", "results.js"), js_dir)
        shutil.copy(Path("static", "img", "favicon.png"), img_dir)
        shutil.copytree(Path(AUDIO_DIR, CURRENT_UUID), Path(audios_dir, CURRENT_UUID))
        
        return {
            "status": "success",
            "message": f"成功接收到文件夹路径",
            "path": f"{export_folder}"
        }
    except Exception as e:
        logger.error(f"导出文件时出错: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "path": ""
        }

def save_html(title: str, data: Dict[str, List[Dict[str, str]]]):
    """保存HTML文件"""
    try:
        import jinja2
        # 读取模板文件
        template = jinja2.Template(open("templates/export_template.html", encoding="utf-8").read())
        html_content = template.render(**data)
        # 保存HTML文件到temp目录
        html_file_path = Path(TEMP_DIR) / f"{title}.html"
        with open(html_file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    except Exception as e:
        logger.error(f"保存HTML文件失败: {e}")
        
def get_local_ips():
    """获取所有有效的本地IP地址"""
    import socket
    ips = []
    try:
        # 尝试创建一个UDP连接来获取本地IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # 连接到一个远程地址（不会真正发送数据）
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            if local_ip not in ips:
                ips.append(local_ip)
                
        # 获取所有网络接口的IP地址
        hostname = socket.gethostname()
        host_ip = socket.gethostbyname(hostname)
        ips.append(host_ip)

    except Exception as e:
        logger.warning(f"获取本地IP地址时出错: {e}")
        
    return ips

def open_browser(url: str):
    """自动打开浏览器访问服务"""
    import webbrowser
    import time
    time.sleep(2) # 等待2秒，确保服务启动完成
    try:
        webbrowser.open(url)
    except Exception as e:
        logger.warning(f"自动打开浏览器时出错: {e}")
        
if __name__ == "__main__":
    import uvicorn
    import threading
    
    try:
        print("--------------------------------------------------")
        
        print("🚀 TingJu 服务启动中...")
        print("👇 可以通过以下地址访问服务:")
        print("💻 本地地址: http://127.0.0.1:51122")
        
        # 获取所有本地IP地址
        local_ips = get_local_ips()
        for ip in local_ips:
            print(f"🌐 网络地址: http://{ip}:51122")
        
        print("--------------------------------------------------")
        
        # 初始化NLTK
        init_nltk()
        
        # 启动浏览器
        threading.Thread(target=open_browser, args=("http://127.0.0.1:51122",), daemon=True).start()
        
        try:
            uvicorn.run(app, host="0.0.0.0", port=51122)
        except KeyboardInterrupt:
            print("👋 TingJu 服务已停止")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
