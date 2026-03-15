import re
from functools import lru_cache
from pathlib import Path

import nltk

from utils.logger import logger

try:
    import pysbd
except ImportError:
    pysbd = None

DATA_DIR = "nltk_data"

PYSBD_LANGUAGE_CODES = {
    'english': 'en',
    'french': 'fr',
    'german': 'de',
    'spanish': 'es',
    'italian': 'it',
    'russian': 'ru',
}

PROTECTED_PATTERNS = (
    r'https?://[^\s<>"\']+|www\.[^\s<>"\']+',
    r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
    r'\b(?:[A-Za-z]\.){2,}',
    r'\b[A-Za-z]*\d+(?:\.\d+){1,}\b',
)

FAST_SPLIT_TEXT_THRESHOLD = 50000

LEADING_CLOSER_PATTERN = re.compile(r'^([\'"”’」』）】\]\}]+[.,!?;:…]*)\s*(.*)$')
PUNCTUATION_FRAGMENT_PATTERN = re.compile(r'^[\'"“”‘’「」『』()\[\]{}<>.,!?;:…]+$')

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
    normalized_text = normalize_text(text=paragraph, lang=lang)
    splitter_input = _prepare_splitter_text(text=normalized_text, lang=lang)

    if lang in ['japanese', 'korean']:
        sentences = _get_sentences_from_ja_ko(text=splitter_input)
    else:
        sentences = _split_sentences(text=splitter_input, lang=lang)

    sentences = _postprocess_sentences(sentences=sentences, lang=lang)
    sentences = [sentence for sentence in sentences if len(sentence) > 2]
    logger.info(f"段落分割完成，共 {len(sentences)} 个句子")
    return sentences


def _split_sentences(text: str, lang: str) -> list[str]:
    """根据语言选择合适的分句器。"""
    if len(text) >= FAST_SPLIT_TEXT_THRESHOLD:
        return _fast_split_sentences(text)

    segmenter = _get_pysbd_segmenter(lang)
    if segmenter is not None:
        try:
            return segmenter.segment(text)
        except Exception as error:
            logger.warning(f"PySBD 分句失败，回退到 NLTK: {error}")

    init_nltk()
    return nltk.sent_tokenize(text=text, language=lang)


def _fast_split_sentences(text: str) -> list[str]:
    """大文本场景下的快速回退分句，优先保证性能。"""
    protected_text, protected_tokens = _protect_text_fragments(text)
    matches = re.findall(r'.+?(?:[.!?]["”’）\]\}]*)(?=\s+|$)|.+$', protected_text)
    return [
        _restore_text_fragments(match.strip(), protected_tokens)
        for match in matches
        if match.strip()
    ]


@lru_cache(maxsize=None)
def _get_pysbd_segmenter(lang: str):
    """缓存 PySBD 分句器，避免重复初始化。"""
    if pysbd is None:
        return None

    language_code = PYSBD_LANGUAGE_CODES.get(lang)
    if language_code is None:
        return None

    try:
        return pysbd.Segmenter(language=language_code, clean=False)
    except ValueError:
        return None

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


def _prepare_splitter_text(text: str, lang: str) -> str:
    """仅为分句器补充必要边界提示，避免污染原始语义。"""
    if lang in ['japanese', 'korean']:
        return text.strip()

    text, protected_tokens = _protect_text_fragments(text)
    text = re.sub(r'([.!?]["\'”’)\]\}]*)(?=(?:["“‘(\[]?[A-ZА-ЯЁ0-9]))', r'\1 ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return _restore_text_fragments(text, protected_tokens)


def _postprocess_sentences(sentences: list[str], lang: str) -> list[str]:
    """修正被错误拆开的尾引号、括号和纯标点碎片。"""
    merged_sentences = []
    for raw_sentence in sentences:
        sentence = raw_sentence.strip()
        if not sentence:
            continue

        sentence = _merge_leading_closers(merged_sentences, sentence)
        if sentence is None:
            continue

        sentence = _finalize_sentence(sentence, lang)
        if sentence:
            merged_sentences.append(sentence)

    return merged_sentences


def _merge_leading_closers(sentences: list[str], sentence: str) -> str | None:
    """把落到下一句开头的右引号、右括号或尾部标点并回前一句。"""
    if not sentences:
        return sentence

    if PUNCTUATION_FRAGMENT_PATTERN.fullmatch(sentence):
        sentences[-1] += sentence
        return None

    match = LEADING_CLOSER_PATTERN.match(sentence)
    if match is None:
        return sentence

    sentences[-1] += match.group(1)
    remainder = match.group(2).strip()
    return remainder or None


def _finalize_sentence(sentence: str, lang: str) -> str:
    """对单个句子做轻量收尾，避免空格落在标点和闭合符号前。"""
    if lang == 'japanese':
        return sentence.strip()

    sentence = re.sub(r'([.!?])\s+(["”’])', r'\1\2', sentence)
    sentence = re.sub(r'\s+([,.;:!?])', r'\1', sentence)
    sentence = re.sub(r'\s+([”’」』）】\]\}])', r'\1', sentence)
    sentence = re.sub(r'([(\[])(\s+)', r'\1', sentence)
    sentence = re.sub(r'\s+', ' ', sentence)
    return sentence.strip()


def _protect_text_fragments(text: str) -> tuple[str, list[str]]:
    """保护 URL、邮箱、缩写链和数字版本号，防止空格调整误伤。"""
    protected_tokens: list[str] = []

    def replace_match(match: re.Match) -> str:
        protected_tokens.append(match.group(0))
        return f"__PROTECTED_TOKEN_{len(protected_tokens) - 1}__"

    for pattern in PROTECTED_PATTERNS:
        text = re.sub(pattern, replace_match, text)

    return text, protected_tokens


def _restore_text_fragments(text: str, protected_tokens: list[str]) -> str:
    """还原被占位符替换的特殊片段。"""
    for index, token in enumerate(protected_tokens):
        text = text.replace(f"__PROTECTED_TOKEN_{index}__", token)
    return text

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

        text, protected_tokens = _protect_text_fragments(text)
        text = re.sub(r'(?<=\D),(?=\S)', r', ', text)
        text = re.sub(r';(?=\S)', r'; ', text)
        text = re.sub(r'(?<!\d):(?=\S)', r': ', text)
        text = re.sub(r'([.!?]["”’）\]\}]*)(?=(?:["“‘(\[]?[A-ZА-ЯЁ0-9]))', r'\1 ', text)
        text = re.sub(r'([.!?])\s+(["”’])', r'\1\2', text)
        text = re.sub(r'\s+([,.;:!?])', r'\1', text)
        text = re.sub(r'([(\[])(\s+)', r'\1', text)
        text = re.sub(r'\s+([”’)\]\}])', r'\1', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = _restore_text_fragments(text, protected_tokens)

    text = re.sub(r'\s+', ' ', text).strip()
    
    return text