from kokoro import KPipeline
import sounddevice as sd
import numpy as np
import torch
# 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
# 🇪🇸 'e' => Spanish es
# 🇫🇷 'f' => French fr-fr
# 🇮🇳 'h' => Hindi hi
# 🇮🇹 'i' => Italian it
# 🇯🇵 'j' => Japanese: pip install misaki[ja]
# 🇧🇷 'p' => Brazilian Portuguese pt-br
# 🇨🇳 'z' => Mandarin Chinese: pip install misaki[zh]
pipeline = KPipeline(lang_code='z', repo_id='hexgrad/Kokoro-82M-v1.1-zh') # <= make sure lang_code matches voice, reference above.
# voice_tensor = torch.load('.\Speak\model\yln\mygf-yln.pth', weights_only=True, map_location=torch.device('cpu')) # Training!
# kokoro haven't push the train code……


def speak(text, speed=1):
    generator = pipeline(
        text, voice='af_maple',
        speed=speed, split_pattern=r'\n+'
    )
    
    audio_chunks = []
    for i, (gs, ps, audio) in enumerate(generator):
        print(f"生成语音段 {i}: {gs}")
        audio_chunks.append(audio)
    
    full_audio = np.concatenate(audio_chunks)

    sd.play(full_audio, samplerate=24000)
    sd.wait()