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
    '——': '-',  # 中文破折号
    '－': '-',  # 中文连字符
    '·': '.',  # 中点
    '…': '...',  # 省略号
}

def init_nltk():
    """初始化 nltk 库, 下载 punkt 词典"""
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
            logger.error(f"punkt 或 punkt_tab 下载失败: {e}")
            raise e
    finally:
        logger.info("nltk 库初始化完成")
    
def get_sentences(paragraph: str) -> list[str]: 
    """将段落分成句子"""
    # 先规范化文本，防止分句错误
    paragraph = normalize_text(paragraph)
    sentences = nltk.sent_tokenize(paragraph)
    # 如果句子字符数少于3个字符，则忽略
    sentences = [s for s in sentences if len(s) > 3]
    logger.info(f"段落分割完成，共 {len(sentences)} 个句子")
    return sentences

def get_words(sentence: str) -> list[str]:
    """将句子分成单词"""
    sentence = normalize_text(sentence)
    words = nltk.word_tokenize(sentence)
    # 如果单词字符数少于2个字符，则忽略
    words = [w for w in words if len(w) > 1]
    logger.info(f"句子分割完成，共 {len(words)} 个单词")
    return words

def normalize_text(text: str) -> str:
    """对文本进行预处理"""
    # 如果有连续的多个空格，则替换成单个空格
    text = re.sub(r"\s+", " ", text)
    # 中文符号替换为英文符号
    for chinese_punct, english_punct in chinese_to_english_punctuation.items():
        text = text.replace(chinese_punct, english_punct)
    # 去除前后空白符
    text = text.strip()
    return text