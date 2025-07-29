import requests
import configparser

config = configparser.ConfigParser()
config.read('.\Think\Config.conf', encoding='utf-8')
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

if __name__ == "__main__":
    # 测试
    print(generate_reply("你好，你是谁？"))