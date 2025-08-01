import nltk
from pathlib import Path

DATA_DIR = "nltk_data"

def init_nltk():
    """初始化 nltk 库, 下载 punkt 词典"""
    nltk_data_dir = Path(DATA_DIR)
    nltk_data_dir.mkdir(exist_ok=True)  
    nltk.data.path.append(str(nltk_data_dir))
    # 检查 punkt 是否存在, 如果不存在则下载
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        # 如果有, 先清理 punkt.zip 和 punkt_tab.zip, 避免出现错误
        punkt_zip = Path(nltk_data_dir, 'tokenizers', 'punkt.zip')
        punkt_tab_zip = Path(nltk_data_dir, 'tokenizers', 'punkt_tab.zip')
        if punkt_zip.exists():
            punkt_zip.unlink()
        if punkt_tab_zip.exists():
            punkt_tab_zip.unlink()
        # 下载 punkt 和 punkt_tab
        nltk.download('punkt', download_dir=DATA_DIR)
        nltk.download('punkt_tab', download_dir=DATA_DIR)
    
def get_sentences(paragraph: str) -> list: 
    """将段落分成句子"""
    sentences = nltk.sent_tokenize(paragraph)
    return sentences

def get_words(sentence: str) -> list:
    words = nltk.word_tokenize(sentence)
    return words