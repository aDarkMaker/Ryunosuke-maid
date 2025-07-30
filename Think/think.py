import os
import requests
import configparser
from Speak.speak import speak
from ASR.control import system_state

current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, 'Config.conf')

config = configparser.ConfigParser()
config.read(config_path, encoding='utf-8')
api_key = config.get('deepseek', 'api_key', fallback='')
persona = config.get('persona', 'description', fallback='')

def generate_reply(user_text):
    print(f"User: {user_text}")
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    if isinstance(user_text, list):
        user_text = user_text[0]['text'] if user_text else ""
    
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
        
        with open("api_errors.log", "a", encoding="utf-8") as f:
            f.write(f"[{time.ctime()}] {error_details}\n")
        
        return error_msg
    
    
    