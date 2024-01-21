import json
import requests
from retry import retry

class RemoteChatAgent:
    def __init__(self, api_key, model_name, history_path, logger):
        self.api_key = api_key
        self.model_name = model_name
        self.history_path = history_path
        self.logger = logger
        self.history = self.init_history()
    
    def init_history(self):
        if self.history_path is not None:
            with open(self.history_path, 'r') as f:
                history = json.load(f)
        else:
            history = []
        return history
    
    @retry(tries=3, delay=2, backoff=2)
    def safe_request(self, url, data, headers):
        response = requests.post(url, json=data, headers=headers)
        return response.json()['choices'][0]['message']['content']
        
    def chat(self, prompt, ID, proxy='AI'):
        message = self.history.copy()
        message.append({
            "role": "user",
            "content": prompt
        })
        data = {
            'model': self.model_name,
            'messages': message
        }
        if proxy == 'AI':
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            url = 'https://api.ai-gaochao.cn/v1/chat/completions'
        if proxy == 'OMG':
            headers = {
                'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            url = 'https://aigptx.top/v1/chat/completions'
        try:
            response = self.safe_request(url, data, headers)
            self.logger.info(f"ID: {ID}:\tSuccessfully made request")
        except Exception as e:
            self.logger.error(f"ID: {ID}:\t{e}")
            response = None
        return response

        
    def export_history(self):
        with open(self.history_path, 'w') as f:
            json.dump(self.history, f)
