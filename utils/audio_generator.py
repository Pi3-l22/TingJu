import asyncio
from pathlib import Path

import edge_tts
from edge_tts import VoicesManager

AUDIO_DIR = "audios"

async def list_voices(language: str = "en") -> list:
    """列出指定语言的可用音色"""
    voices = await VoicesManager.create()
    voices_list = voices.find(Language=language)
    return voices_list

async def generate_audio(text_list: list, voice_name: str, title: str):
    """生成音频(异步)"""
    audio_dir = check_audio_dir(title)
    tasks = []
    for i, text in enumerate(text_list):
        print(text)
        filename = get_filename(text)
        communicate = edge_tts.Communicate(text, voice_name)
        task = communicate.save(f"{audio_dir}/{i+1}_{filename}")
        tasks.append(task)
    await asyncio.gather(*tasks)
    
def generate_audio_sync(text_list: list, voice_name: str, title: str):
    """生成音频(同步)"""
    audio_dir = check_audio_dir(title)
    for i, text in enumerate(text_list):
        filename = get_filename(text)
        communicate = edge_tts.Communicate(text, voice_name)
        communicate.save_sync(f"{audio_dir}/{i+1}_{filename}")

def get_filename(text: str) -> str:
    """根据文本内容生成文件名"""
    # 取前20个字符作为文件名
    if len(text) > 20:
        text = text[:20].strip()
    # 替换文件名中非法的符号
    symbols =[" ", "'", ",", ".", ";", ":", "/", "\\", "|", "*", "?", "\"", "<", ">", "!", "#", "%", "^", "&", "(", ")", "{", "}", "[", "]"]
    for symbol in symbols:
        text = text.replace(symbol, "_")
    filename = f"{text}.mp3"
    return filename

def check_audio_dir(title: str):
    """检查音频目录是否存在"""
    root_dir = Path(AUDIO_DIR)
    root_dir.mkdir(exist_ok=True)
    audio_dir = Path(root_dir, title)
    audio_dir.mkdir(exist_ok=True)
    return audio_dir

