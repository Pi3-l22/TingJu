import asyncio, time
from utils.text_processor import init_nltk, get_sentences
from utils.audio_generator import generate_audio, generate_audio_sync


text = """
Have you ever wondered how technology has changed our lives so dramatically? Just a few decades ago, the idea of carrying a powerful computer in your pocket seemed like science fiction. Now, it's our everyday reality! The famous inventor, Mr. Johnson, once said, "The best way to predict the future is to invent it." This powerful statement continues to inspire innovators around the world. The journey of innovation is not always easy, but it is always rewarding.

The sun is a star at the center of our solar system. It is a nearly perfect sphere of hot plasma. Life on Earth depends on its light and heat. Exploring space helps us understand our place in theuniverse. Future missions aim to discover more about distant planets and galaxies.
"""

def main():
    init_nltk()
    sentences = get_sentences(text)
    voice_name = "en-US-ChristopherNeural"
    # 记录生成时间
    start_time = time.time()
    # 异步生成音频
    asyncio.run(generate_audio(sentences, voice_name, "title"))
    end_time = time.time()
    print("Time taken to generate audio files: ", end_time - start_time, " seconds")

if __name__ == '__main__':
    main()