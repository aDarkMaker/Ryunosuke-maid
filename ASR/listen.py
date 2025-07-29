import sounddevice as sd
import numpy as np
from funasr import AutoModel
import time
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'model')

# 语音活动检测参数
VAD_THRESHOLD = 0.03  # 声音检测阈值 (根据环境调整)
SILENCE_DURATION = 1.5  # 静音持续时间(秒)判定为说话结束

# 流式处理参数
chunk_size = [0, 10, 5]
encoder_chunk_look_back = 4
decoder_chunk_look_back = 1

model = AutoModel(
    model=model_path,
    device="cpu",
    disable_update=True
)


sample_rate = 16000
chunk_stride = chunk_size[1] * 3840  # 每块采样点数

# 状态跟踪变量
is_speaking = False
last_sound_time = time.time()
audio_buffer = []
cache = {}

def calculate_volume(audio_data):
    rms = np.sqrt(np.mean(audio_data**2))
    return rms

def process_audio_buffer(is_final=False):
    if not audio_buffer:
        return

    full_audio = np.concatenate(audio_buffer)
    
    # 调用ASR模型
    res = model.generate(
        input=full_audio,
        cache=cache,
        is_final=is_final,
        chunk_size=chunk_size,
        encoder_chunk_look_back=encoder_chunk_look_back,
        decoder_chunk_look_back=decoder_chunk_look_back
    )
    
    if is_final:
        print("\nfinal:", res)
        with open("log.log", "a", encoding="utf-8") as f:
            f.write(f"[FINAL] {time.ctime()}: {res}\n")
    else:
        print("part:", res)
    
    if is_final:
        audio_buffer.clear()

def callback(indata, frames, time_info, status):
    global is_speaking, last_sound_time
    
    # 提取单声道音频
    speech_chunk = indata[:, 0]
    
    # 计算当前音频块的音量
    current_volume = calculate_volume(speech_chunk)
    
    # 语音活动检测
    if current_volume > VAD_THRESHOLD:
        last_sound_time = time.time()
        
        # 如果从静音状态转为说话状态
        if not is_speaking:
            print("\一有动静...")
            is_speaking = True

        audio_buffer.append(speech_chunk.copy())

        process_audio_buffer(is_final=False)
    
    # 检查是否说话结束
    elif is_speaking:
        silence_time = time.time() - last_sound_time
        if silence_time > SILENCE_DURATION:
            print("Over~")
            is_speaking = False

            if audio_buffer:
                process_audio_buffer(is_final=True)

try:
    with sd.InputStream(samplerate=sample_rate, channels=1, 
                        blocksize=chunk_stride, callback=callback):
        print("I am listening...")
        
        while True:
            sd.sleep(1000)
except KeyboardInterrupt:
    print("\nStoppy！")
except Exception as e:
    print(f"Error: {str(e)}")