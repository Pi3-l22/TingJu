import re
import nltk
from pathlib import Path
from utils.logger import logger

DATA_DIR = "nltk_data"

# 中文符号替换为英文符号
chinese_to_english_punctuation = {
    '“': '"',
    '”': '"',
    '‘': "'",
    '’': "'",
    '（': '(',
    '）': ')',
    '【': '[',
    '】': ']',
    '《': '<',
    '》': '>',
    '？': '?',
    '；': ';',
    '：': ':',
    '，': ',',
    '。': '.',
    '！': '!',
    '——': '-',
    '－': '-',
    '·': '.',
    '...': '…',
}

# 替换为日文符号
to_japanese_punctuation = {
    '...': '…',
    '???': '…',
    '？？？': '…',
    '.': '。',
    '?': '？',
    '!': '！',
    ',': '，',
    '[': '「',
    ']': '」',
    '【': '『',
    '】': '』',
    '(': '（',
    ')': '）',
    '“': '『',
    '”': '』',
    '‘': "「",
    '’': "」",
}

def init_nltk():
    """
    初始化 nltk 库, 下载 punkt 词典
    """
    logger.info("正在初始化 nltk 库...")
    nltk_data_dir = Path(DATA_DIR)
    nltk_data_dir.mkdir(exist_ok=True)  
    nltk.data.path.append(str(nltk_data_dir))
    # 检查 punkt 是否存在, 如果不存在则下载
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        logger.warning("punkt 或 punkt_tab 不存在，开始下载...")
        # 如果有, 先清理 punkt.zip 和 punkt_tab.zip, 避免出现错误
        punkt_zip = Path(nltk_data_dir, 'tokenizers', 'punkt.zip')
        punkt_tab_zip = Path(nltk_data_dir, 'tokenizers', 'punkt_tab.zip')
        if punkt_zip.exists():
            punkt_zip.unlink()
        if punkt_tab_zip.exists():
            punkt_tab_zip.unlink()
        try:
            # 下载 punkt 和 punkt_tab
            nltk.download('punkt', download_dir=DATA_DIR)
            nltk.download('punkt_tab', download_dir=DATA_DIR)
            logger.info("punkt 和 punkt_tab 下载完成")
        except Exception as e:
            logger.error(f"punkt 或 punkt_tab 下载失败，可能与网络情况有关: {e}")
            raise e
    finally:
        logger.info("nltk 库初始化完成")
    
def get_sentences(paragraph: str, lang: str = "english") -> list[str]: 
    """
    将段落分成句子
    
    Args:
        paragraph (str): 待处理的段落
        
    Returns:
        list[str]: 分割后的句子列表
    """
    # 先规范化文本，防止分句错误
    paragraph = normalize_text(text=paragraph, lang=lang)
    
    # 如果语言是日语、韩语，则手动处理分句
    if lang in ['japanese', 'korean']:
        sentences = _get_sentences_from_ja_ko(text=paragraph)
    else:
        sentences = nltk.sent_tokenize(text=paragraph, language=lang)
        
    # 如果句子字符数少于3个字符，则忽略
    sentences = [s for s in sentences if len(s) > 2]
    logger.info(f"段落分割完成，共 {len(sentences)} 个句子")
    return sentences

def _get_sentences_from_ja_ko(text: str) -> list[str]:
    """
    手动处理日语、韩语分句
    
    Args:
        text (str): 待处理的文本

    Returns:
        list[str]: 分割后的句子列表
    """
    dots_pattern = re.compile(r'\.{3,}')  # 匹配三个或更多连续的.
    pattern = re.compile(
        r'(?<=[。！？!?.])'  # 仅在这些符号后断句
        r'(?!\s*[」』（）】\'\"’”])'  # 且后面不能紧跟右括号/右引号
    )
    text = dots_pattern.sub('…', text)
    return [s.strip() for s in pattern.split(text) if s.strip()]

def normalize_text(text: str, lang: str = 'english') -> str:
    """
    对文本进行预处理
    
    Args:
        text (str): 待处理的文本
        
    Returns:
        str: 处理后的文本
    """
    if lang == 'japanese':
        # 符号替换为日文符号
        for punct, japanese_punct in to_japanese_punctuation.items():
            text = text.replace(punct, japanese_punct)
        
        jp_punctuation = r'[。！？、，；：…」』）]'
        text = re.sub(f'({jp_punctuation})\\s+', r'\1', text)
    else:
        # 中文符号替换为英文符号
        for chinese_punct, english_punct in chinese_to_english_punctuation.items():
            text = text.replace(chinese_punct, english_punct)
    
    # 在标点符号后添加空格（除了引号和括号类符号）
    # 处理句号、感叹号、问号后需要空格的情况
    text = re.sub(r'([.!?])([^\s"])', r'\1 \2', text)
    
    # 处理句号、感叹号、问号在引号内的情况，在引号后添加空格
    text = re.sub(r'([.!?])(["\'])', r'\1\2', text)  # 先确保标点和引号紧挨着
    text = re.sub(r'([.!?]["\'])', r'\1 ', text)  # 在引号后添加空格
    
    # 处理括号类符号
    text = re.sub(r'([(){}\[\]<>])', r' \1 ', text)
    
    # 处理逗号、分号、冒号等符号
    text = re.sub(r'([,;:])', r'\1 ', text)
    
    # 处理开头引号前的空格
    text = re.sub(r'\s+"\s+', r' "', text)
    
    # 处理结尾引号后的空格
    text = re.sub(r'"\s+', r'" ', text)
    
    # 处理多余的空格（包括添加空格后产生的多个连续空格）
    text = re.sub(r'\s+', ' ', text)
    
    # 去除前后空白符
    text = text.strip()
    
    return text