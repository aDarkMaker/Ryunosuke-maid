import os
import time
import requests
import configparser
from Speak.speak import speak
from ASR.control import system_state
from MCP import load_tools
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, 'Config.conf')

config = configparser.ConfigParser()
config.read(config_path, encoding='utf-8')
api_key = config.get('deepseek', 'api_key', fallback='')
persona = config.get('persona', 'description', fallback='')

mcp_tools = load_tools()

def clean_speech_text(text):
    return re.sub(r'<\|.*?\|>', '', text).strip()

def generate_reply(user_text):
    if isinstance(user_text, list):
        user_text = user_text[0]['text'] if user_text else ""
        user_text = clean_speech_text(user_text)
        print(f"User: {user_text}")
    
    if user_text.startswith('帮我'):
        if "关机" in user_text :
            speak("帮你了哦，下次记得自己关！")
            if 'ShutDown' in mcp_tools:
                print("执行关机指令...")
                mcp_tools['ShutDown']()
                return "关机指令已执行"
            else:
                return "未找到关机工具"
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": persona},
            {"role": "user", "content": user_text}
        ]
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        resp.raise_for_status()  

        if not resp.content:
            raise ValueError("Empty API response")
            
        reply = resp.json()['choices'][0]['message']['content']
        system_state.pause_listening()
        speak(reply)
        system_state.resume_listening()
        return reply
        
    except Exception as e:
        error_msg = f"API Error: {str(e)}"
        print(error_msg)

        error_details = f"""
        Error: {str(e)}
        Status Code: {getattr(resp, 'status_code', 'N/A')}
        Response: {getattr(resp, 'text', 'No response')[:500]}
        """
        print(error_details)
        return error_msg
    
    
    