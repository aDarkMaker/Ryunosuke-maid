from ASR.listen import sample_rate, chunk_stride
import sounddevice as sd
import threading

def start_listening():
    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, blocksize=chunk_stride):
            print("I am listening...")
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\nStoppy！")
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    # 启动语音监听线程
    listen_thread = threading.Thread(target=start_listening)
    listen_thread.daemon = True
    listen_thread.start()

if __name__ == "__main__":
    main()
