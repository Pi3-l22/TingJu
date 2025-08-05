from typing import List
import translators as ts
from utils.logger import logger

# 翻译器列表
TRANSLATORS = ['bing', 'Sogou', 'baidu', 'Youdao', 'alibaba', 'Caiyun', 'hujiang']
# 默认超时时间
DEFAULT_TIMEOUT = 5

def init_translators():
    ts.preaccelerate_and_speedtest(timeout=float(DEFAULT_TIMEOUT))

def get_text_translated(text_list: List[str], from_lang: str = 'en', to_lang: str = 'zh') -> List[str]:
    """获取文本的翻译, 失败时尝试其他翻译器"""
    logger.info(f"正在翻译 {len(text_list)} 条文本...")
    translated_text = []
    success_count = 0
    for text in text_list:
        translated = None
        # 尝试使用所有翻译器
        for translator in TRANSLATORS:
            try:
                translated = ts.translate_text(
                    text,
                    from_language=from_lang,
                    to_language=to_lang,
                    translator=translator,
                    timeout=float(DEFAULT_TIMEOUT)
                )
                success_count += 1
                break  # 成功就跳出循环
            except Exception as e:
                logger.warning(f"使用 {translator} 翻译 {text} 时失败，原因: {e}")
                continue
        
        if translated is not None:
            translated_text.append(translated)
        else:
            logger.error(f"{text[:20]}... 翻译失败")
            translated_text.append(text + " 翻译失败")

    logger.info(f"共 {success_count}/{len(translated_text)} 条文本翻译完成")
    return translated_text