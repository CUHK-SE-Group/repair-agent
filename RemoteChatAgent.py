import json
import requests

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
    
    def chat(self, prompt, ID):
        message = self.history
        message.append({
            "role": "user",
            "content": prompt
        })
        data = {
            'model': self.model_name,
            'messages': message
        }
        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        response = requests.post(
            'https://aigptx.top/v1/chat/completions', json=data, headers=headers)

        if response.status_code != 200:
            self.logger.error(f"{ID}:\tError making request: {response.text}")
        else:
            self.logger.info(f"{ID}:\tSuccessfully made request")
            return response.json()['choices'][0]['message']['content']
        
    def export_history(self):
        with open(self.history_path, 'w') as f:
            json.dump(self.history, f)
