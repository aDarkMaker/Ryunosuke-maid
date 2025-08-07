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
            speak("帮你了哦，下次记得自己关，不要什么事情都麻烦我！")
            if 'ShutDown' in mcp_tools:
                print("执行关机指令...")
                mcp_tools['ShutDown']()
                return "关机指令已执行"
            else:
                return "未找到关机工具"
        elif "看看" in user_text :
            speak("别急，让我看看！")
            if 'see' in mcp_tools:
                print("执行查看指令...")  
                result = mcp_tools['see']()
                if result.get('success'):
                    text_content = result['data']['full_text']
                    print(f"查看结果: {text_content}")
                return "查看指令已执行"
            else:
                return "未找到查看工具"

    if "天气" in user_text:
        speak("当你感到迷茫的时候不如听听天气预报怎么说！")
        if 'weather' in mcp_tools:
            print("执行天气查询指令...")
            try:
                result = mcp_tools['weather'](userInput=user_text)
                if result and result.get('success'):
                    weather_response = result.get('message', '天气查询失败')
                    print(f"天气查询结果: {weather_response}")
                    
                    system_state.pause_listening()
                    speak(weather_response)
                    system_state.resume_listening()
                    
                    return weather_response
                else:
                    error_msg = result.get('error', '天气查询失败') if result else '天气查询失败'
                    print(f"天气查询失败: {error_msg}")
                    
                    system_state.pause_listening()
                    speak(f"抱歉，天气查询失败了：{error_msg}")
                    system_state.resume_listening()
                    
                    return f"天气查询失败: {error_msg}"
            except Exception as e:
                error_msg = f"天气查询异常: {str(e)}"
                print(error_msg)
                
                system_state.pause_listening()
                speak("抱歉，天气查询出现了问题")
                system_state.resume_listening()
                
                return error_msg
        else:
            return "未找到天气查询工具"
    
    if "几点" in user_text or "几号" in user_text :
        if 'time' in mcp_tools:
            print("执行时间查询指令...")
            result = mcp_tools['time']()
            if result and result.get('success'):
                time_response = result.get('message', '时间查询失败')
                print(f"时间查询结果: {time_response}")
                speak(time_response)
                return time_response  
        
    
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
    
    
    