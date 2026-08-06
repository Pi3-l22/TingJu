from typing import List
import os
from threading import Lock
from utils.logger import logger

# 翻译器列表
TRANSLATORS = ['bing', 'sogou', 'youdao', 'alibaba', 'hujiang', 'iflyrec', 'caiyun', 'itranslate', 'lingvanex', 'translateCom', 'yandex']
# alibaba apertium bing caiyun google hujiang iflyrec itranslate languageWire lingvanex modernMt myMemory qqTranSmart reverso sogou sysTran translateCom utibet yandex youdao
# alibaba apertium bing hujiang iflyrec itranslate languageWire lingvanex qqTranSmart sogou sysTran translateCom utibet yandex youdao

# 默认超时时间
DEFAULT_TIMEOUT = 5.0
_translators_module = None
_translators_error = None
_translation_disabled = False
_translators_lock = Lock()


def _load_translators():
    """Load translators only when a translation request is made.

    translators 6.x performs a geolocation request during import unless a
    region is configured.  That network probe must never be part of app
    startup, and a blocked network must degrade to the original text.
    """
    global _translators_module, _translators_error
    with _translators_lock:
        if _translators_module is not None:
            return _translators_module
        if _translators_error is not None:
            return None

        configured_region = os.environ.get("translators_default_region", "").strip().upper()
        requested_region = os.environ.get("TINGJU_TRANSLATORS_REGION", "CN").strip().upper()
        if configured_region not in {"CN", "EN"}:
            configured_region = requested_region if requested_region in {"CN", "EN"} else "CN"
            os.environ["translators_default_region"] = configured_region
        try:
            import translators as ts
        except Exception as error:
            _translators_error = error
            logger.warning("翻译引擎不可用，将保留原文: %s", error)
            return None

        _translators_module = ts
        return ts


def _is_network_failure(error: Exception) -> bool:
    message = str(error).lower()
    return any(
        marker in message
        for marker in (
            "winerror 10013",
            "unable to connect the internet",
            "connection refused",
            "connection reset",
            "max retries exceeded",
            "timed out",
            "timeout",
        )
    )

def init_translators():
    global _translation_disabled
    ts = _load_translators()
    if ts is not None:
        try:
            ts.preaccelerate_and_speedtest(timeout=DEFAULT_TIMEOUT)
        except Exception as error:
            _translation_disabled = True
            logger.warning("翻译引擎测速失败，将保留原文: %s", error)

def get_text_translated(text_list: List[str], from_lang: str = 'en', to_lang: str = 'zh') -> List[str]:
    """
    获取文本的翻译, 失败时尝试其他翻译器
    
    Args:
        text_list (List[str]): 需要翻译的文本列表
        from_lang (str, optional): 源语言。默认为 'en'。
        to_lang (str, optional): 目标语言。默认为 'zh'。

    Returns:
        List[str]: 翻译后的文本列表
    """
    logger.info(f"正在翻译 {len(text_list)} 条文本...")
    global _translation_disabled
    ts = _load_translators()
    if ts is None:
        return list(text_list)
    if _translation_disabled:
        return list(text_list)

    translated_text = []
    success_count = 0
    for index, text in enumerate(text_list):
        if _translation_disabled:
            translated_text.extend(text_list[index:])
            break
        translated = None
        # 尝试使用所有翻译器
        for translator in TRANSLATORS:
            try:
                translated = ts.translate_text(
                    text,
                    from_language=from_lang,
                    to_language=to_lang,
                    translator=translator,
                    timeout=DEFAULT_TIMEOUT
                )
                success_count += 1
                break  # 成功就跳出循环
            except Exception as e:
                logger.warning(f"使用 {translator} 翻译 {text} 时失败，原因: {e}")
                if _is_network_failure(e):
                    _translation_disabled = True
                    logger.warning("翻译网络不可用，本次及后续请求将保留原文")
                    break
                continue
        
        if translated is not None:
            translated_text.append(translated)
        elif _translation_disabled:
            translated_text.append(text)
        else:
            logger.error(f"{text[:20]}... 翻译失败")
            translated_text.append(text + " 翻译失败")

    logger.info(f"共 {success_count}/{len(translated_text)} 条文本翻译完成")
    return translated_text
