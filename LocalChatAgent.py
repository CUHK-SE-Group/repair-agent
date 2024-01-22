import json
from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer
import torch

class LocalChatAgent:
    def __init__(self, model_dir, model_name, history_path, logger):
        self.model_dir = model_dir
        self.model_name = model_name
        self.history_path = history_path
        self.logger = logger
        self.model_path = f"{self.model_dir}/{self.model_name}"
        self.model =  AutoModelForCausalLM.from_pretrained(self.model_path, 
                                                           device_map='auto', 
                                                           low_cpu_mem_usage=True, 
                                                           torch_dtype=torch.float16) # half-precision
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, 
                                                        padding_side="left", 
                                                        use_fast=False)
        self.streamer = TextStreamer(self.tokenizer, 
                                        skip_prompt=True, 
                                        skip_special_tokens=True)
        self.history_ids = self.init_history()

    def encode(self, prompt):
        input_ids = self.tokenizer(prompt, 
                                    return_tensors="pt", 
                                    add_special_tokens=False).input_ids.cuda()
        return input_ids
    
    def generate(self, input_ids, streamer):
        output_ids = self.model.generate(input_ids, 
                                    streamer=streamer,
                                    max_new_tokens=8192, 
                                    do_sample = True, 
                                    top_k = 30, 
                                    top_p = 0.85, 
                                    temperature = 0.5, 
                                    repetition_penalty=1.,
                                    pad_token_id = self.tokenizer.eos_token_id,)
        return output_ids
    
    def decode(self, output_ids):
        response = self.tokenizer.batch_decode(output_ids, 
                                    skip_special_tokens=True, 
                                    clean_up_tokenization_spaces=False)[0].split('[/INST]')[-1].strip()
        return response

    def init_history(self):
        history_ids = self.encode('<s>')
        if self.history_path is not None:
            with open(self.history_path, 'r') as f:
                history = json.load(f)
                for message in history:
                    if message['role'] == 'user':
                        history_ids = torch.concat([history_ids, 
                                                    self.encode("[INST]"), 
                                                    self.encode(message['content'].strip()), 
                                                    self.encode("[/INST]")], dim=-1)
                    else:
                        history_ids = torch.concat([history_ids,
                                                    self.encode(message['content'].strip()),
                                                    self.encode('</s>')], dim=-1)
        return history_ids
    
    def chat(self, prompt, ID, proxy='batch'):
        input_ids = torch.concat([self.history_ids.clone(), 
                                self.encode("[INST]"), 
                                self.encode(prompt.strip()), 
                                self.encode("[/INST]")], dim=-1)
        response = None
        if proxy == 'stream':
            output_ids = self.generate(input_ids, self.streamer)
        elif proxy == 'batch':
            output_ids = self.generate(input_ids, None)
        else:
            raise ValueError("proxy must be 'stream' or 'batch'")
        response = self.decode(output_ids)
        self.logger.info(f"ID: {ID}:\tSuccessfully generated response")
        return response
