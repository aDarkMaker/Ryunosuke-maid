from kokoro import KPipeline
import sounddevice as sd
import numpy as np
# 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
# 🇪🇸 'e' => Spanish es
# 🇫🇷 'f' => French fr-fr
# 🇮🇳 'h' => Hindi hi
# 🇮🇹 'i' => Italian it
# 🇯🇵 'j' => Japanese: pip install misaki[ja]
# 🇧🇷 'p' => Brazilian Portuguese pt-br
# 🇨🇳 'z' => Mandarin Chinese: pip install misaki[zh]
pipeline = KPipeline(lang_code='z', repo_id='hexgrad/Kokoro-82M') # <= make sure lang_code matches voice, reference above.

def speak(text, voice='af_heart', speed=1):
    generator = pipeline(
        text, voice=voice,
        speed=speed, split_pattern=r'\n+'
    )
    
    audio_chunks = []
    for i, (gs, ps, audio) in enumerate(generator):
        print(f"生成语音段 {i}: {gs}")
        audio_chunks.append(audio)
    
    # 合并所有音频片段
    full_audio = np.concatenate(audio_chunks)
    
    # 直接播放音频
    print("播放语音...")
    sd.play(full_audio, samplerate=24000)
    sd.wait()  # 等待播放完成
    print("播放结束")