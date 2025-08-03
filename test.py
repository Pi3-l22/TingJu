import asyncio, time
from utils.text_processor import init_nltk, get_sentences
from utils.audio_generator import generate_audio, list_voices
from utils.text_translator import get_text_translated
from utils.file_processor import extract_text_from_file
from utils.logger import logger

def test_processor():
    # # 初始化 nltk
    # init_nltk()
    # # 记录生成时间
    # start_time = time.time()
    # text = extract_text_from_file('./test_files/a.txt')
    # print(text)
    # print()
    # sentences = get_sentences(text)
    # for sentence in sentences:
    #     print(sentence)

    # # 翻译
    # translated_text = get_text_translated(sentences)
    # for i, t in enumerate(translated_text):
    #     logger.info(f"翻译结果 {i+1}: {t}")
    
    # # 发音
    # voice_name = "en-US-ChristopherNeural"
    # logger.info("开始生成音频文件")
    # # 异步生成音频
    # asyncio.run(generate_audio(sentences, voice_name, "title"))
    # end_time = time.time()
    # logger.info(f"耗时: {end_time - start_time:.2f} 秒")
    asyncio.run(list_voices())

if __name__ == '__main__':
    test_processor()