import requests
import time
from retry import retry

class RemoteChatter:
    def __init__(self, api_key, model='gpt-3.5-turbo'):
        self.api_key = api_key
        self.model = model

    @retry(tries=3, delay=2, backoff=2)
    def safe_request(self, url, data, headers):
        response = requests.post(url, json=data, headers=headers)
        # print(response.json())
        # exit()
        return response.json()
        
    def chat(self, prompt, ID, proxy='AI', temperature=0.0):
        data = {
            'model': self.model,
            'messages': prompt,
            'temperature': temperature
        }
        if proxy == 'AI':
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            url = 'https://api.openai.com/v1/chat/completions'
        elif proxy == 'OMG':
            headers = {
                'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            url = 'https://aigptx.top/v1/chat/completions'
        else:
            raise ValueError("proxy must be 'AI' or 'OMG'")
        ti = 0
        while ti <= 10:
            response_api = self.safe_request(url, data, headers)
            try:
                response = response_api['choices'][0]['message']['content']
                print(f"ID: {ID}:\tSuccessfully made request")
                break
            except Exception as e:
                print(f"ID: {ID}:\t{response_api}")
                response = None
                ti += 1
                time.sleep(3)
        return response