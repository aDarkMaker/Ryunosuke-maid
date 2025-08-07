from ASR.listen import start_listening
from Speak.speak import speak

def main():
    print("Start...")
    speak("今天也是元气满满的一天呢！")
    try:
        start_listening()  # 开始监听
    except KeyboardInterrupt:
        print("\n程序退出")

if __name__ == "__main__":
    main()
