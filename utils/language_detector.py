from langdetect import detect, detect_langs
from langdetect.lang_detect_exception import LangDetectException
from utils.logger import logger

# 语言代码映射表
LANGUAGE_CODES = {
    'en': 'english',     # 英语
    'fr': 'french',      # 法语
    'de': 'german',      # 德语
    'ja': 'japanese',    # 日语
    'ko': 'korean',      # 韩语
    'ru': 'russian',     # 俄语
    'es': 'spanish',     # 西班牙语
    'pt': 'portuguese',  # 葡萄牙语
    'it': 'italian'      # 意大利语
}

LANGUAGE_NAMES= {
    'en': '英语',
    'fr': '法语',
    'de': '德语',
    'ja': '日语',
    'ko': '韩语',
    'ru': '俄语',
    'es': '西班牙语',
    'pt': '葡萄牙语',
    'it': '意大利语'
}

# TTS地区代码映射表
TTS_LOCALES = {
    'en': 'en-US',     # 英语(美国)
    'fr': 'fr-FR',     # 法语(法国)
    'de': 'de-DE',     # 德语(德国)
    'ja': 'ja-JP',     # 日语(日本)
    'ko': 'ko-KR',     # 韩语(韩国)
    'ru': 'ru-RU',     # 俄语(俄罗斯)
    'es': 'es-ES',     # 西班牙语(西班牙)
    'pt': 'pt-PT',     # 葡萄牙语(葡萄牙)
    'it': 'it-IT',     # 意大利语(意大利)
}

def detect_language(text: str) -> dict:
    """
    检测文本语言
    
    Args:
        text (str): 待检测的文本
        
    Returns:
        dict: error错误信息 code语言代码 name语言名称 locale地区代码
    """
    try:
        # 检测最可能的语言
        detected_lang = detect(text)
        
        # 获取所有可能的语言及其概率
        # lang_probs = detect_langs(text)
        
        # 判断语言是否为中文
        if detected_lang == 'zh-cn':
            return {
                'error': '识别到语言类型为zh-cn，不支持学习中文，若识别错误，请手动选择语言类型',
                'code': None,
                'name': None,
                'locale': None
            }

        # 判断语言是否在语言代码列表中
        if detected_lang not in LANGUAGE_CODES:
            return {
                'error': f'不支持语言类型{detected_lang}，若识别错误，请手动选择语言类型',
                'code': None,
                'name': None,
                'locale': None
            }
        
        # 通过语言获取TTS地区代码
        tts_locale = TTS_LOCALES.get(detected_lang, '')
        if tts_locale == '':
            return {
                'error': f'语言类型 {detected_lang} 没有兼容的TTS地区代码',
                'code': None,
                'name': None,
                'locale': None
            }
        
        return {
            'error': None,
            'code': detected_lang,
            'name': LANGUAGE_CODES.get(detected_lang, detected_lang),
            'locale': tts_locale
        }
    except LangDetectException as e:
        logger.error(f"语言类型检测失败: {str(e)}")
        return {
            'error': '无法检测出文本的语言类型，请检查文本并手动选择语言类型',
            'code': None,
            'name': None,
            'locale': None
        }
    except Exception as e:
        logger.error(f"语言类型检测过程中发生错误: {str(e)}")
        return {
            'error': '语言类型检测过程出错，，请检查文本并手动选择语言类型',
            'code': None,
            'name': None,
            'locale': None
        }