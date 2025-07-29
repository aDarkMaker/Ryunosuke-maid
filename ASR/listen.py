import sounddevice as sd
import numpy as np
from funasr import AutoModel

chunk_size = [0, 10, 5]
encoder_chunk_look_back = 4
decoder_chunk_look_back = 1

model = AutoModel(
    model="./ASR/model",
    trust_remote_code=True,
    device="cpu"
)

sample_rate = 16000  # 采样率
chunk_stride = chunk_size[1] * 960  # 每块采样点数

cache = {}

def callback(indata, frames, time, status):
    speech_chunk = indata[:, 0]
    res = model.generate(
        input=speech_chunk,
        cache=cache,
        is_final=False,
        chunk_size=chunk_size,
        encoder_chunk_look_back=encoder_chunk_look_back,
        decoder_chunk_look_back=decoder_chunk_look_back
    )
    print(res)

with sd.InputStream(samplerate=sample_rate, channels=1, blocksize=chunk_stride, callback=callback):
    print("I am listening...")
    while True:
        sd.sleep(1000)