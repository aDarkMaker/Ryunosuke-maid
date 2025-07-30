import threading

# 全局状态管理器
class SystemState:
    def __init__(self):
        self.listening_active = True
        self.lock = threading.Lock()
    
    def pause_listening(self):
        with self.lock:
            self.listening_active = False
            print("监听已暂停")
    
    def resume_listening(self):
        with self.lock:
            self.listening_active = True
            print("监听已恢复")
    
    def is_listening_active(self):
        with self.lock:
            return self.listening_active

# 全局状态实例
system_state = SystemState()