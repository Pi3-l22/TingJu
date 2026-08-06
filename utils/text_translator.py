import os
import re
from threading import Lock
from typing import List, Tuple

from utils.logger import logger

# 翻译器列表
# Keep the no-key providers that currently support English-to-Chinese text.
# Bing and Sogou are intentionally excluded: Bing's HTML parser is broken in
# the current translators release and Sogou starts returning anti-abuse tokens
# after a small number of requests.
TRANSLATORS = [
    'youdao',
    'alibaba',
    'iflyrec',
    'caiyun',
    'itranslate',
    'lingvanex',
    'translateCom',
]

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

def _is_valid_translation(value: object, source: str, to_lang: str) -> bool:
    """Reject successful HTTP responses that are not actual translations."""
    if not isinstance(value, str):
        return False

    translated = value.strip()
    if not translated:
        return False

    lowered = translated.lower()
    if (
        translated.startswith('<')
        or translated.startswith('{')
        or 'captcha' in lowered
        or 'verify' in lowered
        or 'access denied' in lowered
    ):
        return False

    # Sogou's anti-abuse response is a compact lower-case alpha-numeric token.
    if re.fullmatch(r'[a-z0-9]{16,64}', translated):
        return False

    source_words = re.findall(r'[A-Za-z]+', source)
    if to_lang.lower().startswith('zh') and len(source_words) >= 2 and len(source) >= 12:
        # A full English sentence translated to Chinese should contain at least
        # one Han character. This catches unchanged/error responses while still
        # allowing short proper nouns and numeric-only input.
        if not re.search(r'[\u3400-\u9fff]', translated):
            return False
        if translated.casefold() == source.strip().casefold():
            return False

    return True


def get_text_translated(
    text_list: List[str], from_lang: str = 'en', to_lang: str = 'zh'
) -> Tuple[List[str], str]:
    """
    获取文本的翻译, 失败时尝试其他翻译器
    
    Args:
        text_list (List[str]): 需要翻译的文本列表
        from_lang (str, optional): 源语言。默认为 'en'。
        to_lang (str, optional): 目标语言。默认为 'zh'。

    Returns:
        Tuple[List[str], str]: 对齐的翻译列表和警告信息
    """
    logger.info(f"正在翻译 {len(text_list)} 条文本...")
    global _translation_disabled
    ts = _load_translators()
    if ts is None:
        return list(text_list), "翻译引擎不可用，已保留原文"
    if _translation_disabled:
        return list(text_list), "翻译网络不可用，已保留原文"

    translated_text = []
    failed_numbers = []
    disabled_translators = set()
    preferred_translator = None
    provider_successes = {translator: 0 for translator in TRANSLATORS}
    success_count = 0
    for index, text in enumerate(text_list, start=1):
        translated = None
        order = []
        if preferred_translator and preferred_translator not in disabled_translators:
            order.append(preferred_translator)
        order.extend(
            translator for translator in TRANSLATORS
            if translator not in disabled_translators and translator not in order
        )

        for translator in order:
            try:
                candidate = ts.translate_text(
                    text,
                    from_language=from_lang,
                    to_language=to_lang,
                    translator=translator,
                    timeout=DEFAULT_TIMEOUT
                )
                if not _is_valid_translation(candidate, text, to_lang):
                    disabled_translators.add(translator)
                    logger.warning(
                        "翻译引擎 %s 返回无效结果，当前批次已熔断（第 %s 句）",
                        translator,
                        index,
                    )
                    continue
                translated = candidate.strip()
                preferred_translator = translator
                provider_successes[translator] += 1
                success_count += 1
                break
            except Exception as e:
                disabled_translators.add(translator)
                logger.warning(
                    "翻译引擎 %s 失败（第 %s 句），当前批次已熔断：%s",
                    translator,
                    index,
                    e,
                )
                continue

        if translated is not None:
            translated_text.append(translated)
        else:
            translated_text.append(text)
            failed_numbers.append(index)
            logger.error("第 %s 句翻译失败，已保留原文", index)

    warning_msg = ""
    if failed_numbers:
        warning_msg = (
            f"第 {','.join(map(str, failed_numbers))} 句翻译失败，已保留原文；"
            "请检查网络或稍后重试"
        )

    used_summary = ', '.join(
        f"{translator}:{count}"
        for translator, count in provider_successes.items()
        if count
    ) or 'none'
    logger.info(
        "翻译完成：%s/%s 成功，失败句号=%s，使用引擎=%s",
        success_count,
        len(translated_text),
        ','.join(map(str, failed_numbers)) or 'none',
        used_summary,
    )
    return translated_text, warning_msg
