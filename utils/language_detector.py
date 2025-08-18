from langdetect import detect, detect_langs
from langdetect.lang_detect_exception import LangDetectException
# from utils.logger import logger

# 语言代码映射表
LANGUAGE_CODES = {
    'en': 'English',     # 英语
    'zh-cn': 'Chinese',  # 中文
    'fr': 'French',      # 法语
    'de': 'German',      # 德语
    'es': 'Spanish',     # 西班牙语
    'ja': 'Japanese',    # 日语
    'ko': 'Korean',      # 韩语
    'ru': 'Russian',     # 俄语
    'pt': 'Portuguese',  # 葡萄牙语
    'it': 'Italian'      # 意大利语
}

# TTS地区代码映射表
TTS_LOCALES = {
    'en': 'en-US',     # 英语(美国)
    'zh-cn': 'zh-CN',  # 中文(大陆)
    'fr': 'fr-FR',     # 法语(法国)
    'de': 'de-DE',     # 德语(德国)
    'es': 'es-ES',     # 西班牙语(西班牙)
    'ja': 'ja-JP',     # 日语(日本)
    'ko': 'ko-KR',     # 韩语(韩国)
    'ru': 'ru-RU',     # 俄语(俄罗斯)
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

        # 判断语言是否在语言代码列表中
        if detected_lang not in LANGUAGE_CODES:
            return {
                'error': f'语言类型 {detected_lang} 不支持',
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
        # logger.error(f"语言类型检测失败: {str(e)}")
        return {
            'error': '无法检测出文本的语言类型',
            'code': None,
            'name': None,
            'locale': None
        }
    except Exception as e:
        # logger.error(f"语言类型检测过程中发生错误: {str(e)}")
        return {
            'error': '语言类型检测过程出错',
            'code': None,
            'name': None,
            'locale': None
        }