import os
import requests
import configparser

current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, 'Config.conf')

config = configparser.ConfigParser()
config.read(config_path, encoding='utf-8')
api_key = config.get('deepseek', 'api_key', fallback='')
persona = config.get('persona', 'description', fallback='')

def generate_reply(user_text):
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
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code == 200:
        return resp.json()['choices'][0]['message']['content']
    else:
        return f"api_Error: {resp.status_code}"