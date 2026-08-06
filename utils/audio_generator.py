import asyncio
import hashlib
from pathlib import Path
from typing import List, Optional, Tuple

import edge_tts
from edge_tts import VoicesManager
from utils.logger import logger
from utils.runtime import DATA_DIR

AUDIO_DIR = DATA_DIR / "audios"
AUDIO_MAX_CONCURRENCY = 4
AUDIO_MAX_ATTEMPTS = 2
AUDIO_RETRY_DELAY = 0.5

async def list_voices(locale: str = 'en-US') -> list:
    """
    列出指定语言的可用音色
    
    Args:
        locale (str, optional): 语言代码，如 en-US。默认为 'en-US'
        
    Returns:
        list: 音色列表
    """
    logger.info(f"正在获取 {locale} 语言的音色列表...")
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
    logger.info(f"共找到 {locale} 语言的 {len(voices_list)} 个可用音色")
    return voices_list

async def _generate_one_audio(
    index: int,
    text: str,
    voice_name: str,
    audio_dir: Path,
    semaphore: asyncio.Semaphore,
) -> Tuple[int, Optional[str], Optional[Exception]]:
    filename = f"{index + 1}_{_get_filename(text)}"
    file_path = Path(audio_dir, filename)

    async with semaphore:
        for attempt in range(1, AUDIO_MAX_ATTEMPTS + 1):
            try:
                communicate = edge_tts.Communicate(text, voice_name)
                await communicate.save(str(file_path))
                if not _is_valid_mp3(file_path):
                    raise ValueError("生成的文件不是有效的 MP3")
                return index, filename, None
            except Exception as error:
                try:
                    file_path.unlink(missing_ok=True)
                except OSError:
                    pass
                if attempt < AUDIO_MAX_ATTEMPTS:
                    await asyncio.sleep(AUDIO_RETRY_DELAY)
                else:
                    return index, None, error

    return index, None, RuntimeError("音频任务未完成")


async def generate_audio(
    text_list: List[str], voice_name: str, title: str
) -> Tuple[Path, List[Optional[str]], str]:
    """
    生成音频(异步)
    
    Args:
        text_list (List[str]): 文本列表
        voice_name (str): 音色名称
        title (str): 标题，用于生成音频目录名称
        
    Returns:
        Tuple[Path, List[Optional[str]], str]: 返回音频目录路径、对齐的文件名列表和警告信息
    """
    logger.info(f"正在生成音频文件，音色为 {voice_name} ...")
    audio_dir = _check_audio_dir(title)
    filenames: List[Optional[str]] = [None] * len(text_list)
    semaphore = asyncio.Semaphore(AUDIO_MAX_CONCURRENCY)
    tasks = [
        asyncio.create_task(
            _generate_one_audio(i, text, voice_name, audio_dir, semaphore)
        )
        for i, text in enumerate(text_list)
    ]
    results = await asyncio.gather(*tasks)

    warning_num = []
    success_count = 0
    for index, filename, error in results:
        if error is not None or filename is None:
            warning_num.append(index + 1)
            logger.error("生成第 %s 个音频时出错: %s", index + 1, error)
        else:
            filenames[index] = filename
            success_count += 1

    warning_msg = ""
    if warning_num:
        warning_msg = (
            f"第 {','.join(map(str, warning_num))} 个音频生成失败，"
            "请检查网络或尝试换个音色重新生成"
        )

    logger.info(
        "音频生成完成：%s/%s 成功，失败序号=%s，保存在 %s",
        success_count,
        len(text_list),
        ','.join(map(str, warning_num)) or 'none',
        audio_dir,
    )
    return audio_dir, filenames, warning_msg
    
def generate_audio_sync(
    text_list: List[str], voice_name: str, title: str
) -> Tuple[Path, List[Optional[str]]]:
    """
    生成音频(同步)
    
    Args:
        text_list (List[str]): 文本列表
        voice_name (str): 音色名称
        title (str): 标题，用于生成音频目录名称
        
    Returns:
        Tuple[Path, List[Optional[str]]]: 音频目录路径和对齐的文件名列表
    """
    logger.info(f"正在生成音频文件，音色为 {voice_name} ...")
    audio_dir = _check_audio_dir(title)
    filenames: List[Optional[str]] = [None] * len(text_list)
    success_count = 0
    for i, text in enumerate(text_list):
        filename = f"{i+1}_{_get_filename(text)}"
        file_path = Path(audio_dir, filename)
        try:
            communicate = edge_tts.Communicate(text, voice_name)
            communicate.save_sync(str(file_path))
            if not _is_valid_mp3(file_path):
                raise ValueError("生成的文件不是有效的 MP3")
            filenames[i] = filename
            success_count += 1
        except Exception as e:
            logger.error(f"生成第 {i+1} 个音频时出错: {e}")
            try:
                file_path.unlink(missing_ok=True)
            except OSError:
                pass
    logger.info(f"共 {success_count}/{len(text_list)} 条音频生成完成，保存在 {audio_dir}")
    return audio_dir, filenames

def _get_filename(text: str) -> str:
    """根据文本内容生成文件名"""
    # 去除文本前后的空白字符，确保相同的实际内容生成相同的文件名
    stripped_text = text.strip()
    
    # 使用文本的MD5哈希值作为文件名，确保相同文本对应相同文件名
    text_hash = hashlib.md5(stripped_text.encode('utf-8')).hexdigest()
    filename = f"{text_hash}.mp3"
    return filename


def _is_valid_mp3(file_path: Path) -> bool:
    """Check that edge-tts produced a non-empty MP3 rather than a partial file."""
    try:
        if file_path.stat().st_size < 4:
            return False
        with file_path.open("rb") as audio_file:
            header = audio_file.read(4)
    except OSError:
        return False

    return header[:3] == b"ID3" or (
        header[0] == 0xFF and (header[1] & 0xE0) == 0xE0
    )

def _check_audio_dir(title: str):
    """检查音频目录是否存在"""
    root_dir = Path(AUDIO_DIR)
    root_dir.mkdir(parents=True, exist_ok=True)
    audio_dir = Path(root_dir, title)
    audio_dir.mkdir(parents=True, exist_ok=True)
    return audio_dir
