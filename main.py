from ASR.listen import start_listening

def main():
    print("Start...")
    try:
        start_listening()  # 开始监听
    except KeyboardInterrupt:
        print("\n程序退出")

if __name__ == "__main__":
    main()
