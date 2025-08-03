import asyncio
import hashlib
from pathlib import Path
from typing import List, Tuple

import edge_tts
from edge_tts import VoicesManager
from utils.logger import logger

AUDIO_DIR = "audios"

async def list_voices(locale: str = 'en-US') -> list:
    """列出指定语言的可用音色"""
    voices_list = []
    voices = await VoicesManager.create()
    _voices_list = voices.find(Locale=locale)
    for voice in _voices_list:
        voices_list.append({
            "name": voice["ShortName"],
            "gender": voice["Gender"],
            # VoiceTag': {'ContentCategories': ['Conversation', 'Copilot'], 'VoicePersonalities': ['Expressive', 'Caring', 'Pleasant', 'Friendly']}
            "style": voice["VoiceTag"]["ContentCategories"] + voice["VoiceTag"]["VoicePersonalities"],
        })
    logger.info(f"共找到 '{locale}' 语言的 {len(voices_list)} 个可用音色")
    return voices_list

async def generate_audio(text_list: List[str], voice_name: str, title: str) -> Tuple[Path, List[str]]:
    """生成音频(异步)，返回音频目录路径和生成的文件名列表"""
    audio_dir = _check_audio_dir(title)
    filenames = []
    tasks = []
    for i, text in enumerate(text_list):
        filename = _get_filename(text)
        filenames.append(f"{i+1}_{filename}")
        file_path = Path(audio_dir, filenames[-1])
        communicate = edge_tts.Communicate(text, voice_name)
        task = asyncio.create_task(communicate.save(str(file_path)))
        tasks.append(task)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 检查执行结果，记录任何可能的异常
    success_count = 0
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"生成第 {i+1} 个音频时出错: {result}")
        else:
            success_count += 1
    
    logger.info(f"{success_count}/{len(text_list)} 条音频生成完成，音色为 {voice_name}，保存在 {audio_dir}")
    return audio_dir, filenames
    
def generate_audio_sync(text_list: List[str], voice_name: str, title: str) -> Tuple[Path, List[str]]:
    """生成音频(同步)，返回音频目录路径和生成的文件名列表"""
    audio_dir = _check_audio_dir(title)
    filenames = []
    success_count = 0
    for i, text in enumerate(text_list):
        try:
            filename = _get_filename(text)
            filenames.append(f"{i+1}_{filename}")
            communicate = edge_tts.Communicate(text, voice_name)
            file_path = Path(audio_dir, filenames[-1])
            communicate.save_sync(str(file_path))
            success_count += 1
        except Exception as e:
            logger.error(f"生成第 {i+1} 个音频时出错: {e}")
    logger.info(f"{success_count}/{len(text_list)} 条音频生成完成，音色为 {voice_name}，保存在 {audio_dir}")
    return audio_dir, filenames

def _get_filename(text: str) -> str:
    """根据文本内容生成文件名"""
    # 去除文本前后的空白字符，确保相同的实际内容生成相同的文件名
    stripped_text = text.strip()
    
    # 使用文本的MD5哈希值作为文件名，确保相同文本对应相同文件名
    text_hash = hashlib.md5(stripped_text.encode('utf-8')).hexdigest()
    filename = f"{text_hash}.mp3"
    return filename

def _check_audio_dir(title: str):
    """检查音频目录是否存在"""
    root_dir = Path(AUDIO_DIR)
    root_dir.mkdir(exist_ok=True)
    audio_dir = Path(root_dir, title)
    audio_dir.mkdir(exist_ok=True)
    return audio_dir