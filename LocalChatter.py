from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer
import torch

class LocalChatter:
    def __init__(self, dir, model):
        self.model_dir = dir
        self.model_name = model
        self.model_path = f"{self.model_dir}/{self.model_name}"
        self.model =  AutoModelForCausalLM.from_pretrained(self.model_path, 
                                                           device_map='auto', 
                                                           low_cpu_mem_usage=True, 
                                                           torch_dtype=torch.float16) # half-precision
                                                            #   torch_dtype=torch.float32) # single-precision
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, 
                                                        padding_side="left", 
                                                        use_fast=False)
        self.streamer = TextStreamer(self.tokenizer, 
                                        skip_prompt=True, 
                                        skip_special_tokens=True)

    def encode(self, prompt):
        input_ids = self.tokenizer(prompt, 
                                    return_tensors="pt", 
                                    add_special_tokens=False).input_ids.cuda()
        return input_ids
    
    def generate(self, input_ids, streamer, temperature=0.0):
        output_ids = self.model.generate(input_ids, 
                                    streamer=streamer,
                                    max_new_tokens=8192, 
                                    do_sample = True, 
                                    top_k = 30, 
                                    top_p = 0.85, 
                                    temperature = temperature, 
                                    repetition_penalty=1.,
                                    pad_token_id = self.tokenizer.eos_token_id,)
        return output_ids
    
    def decode(self, output_ids):
        response = self.tokenizer.batch_decode(output_ids, 
                                    skip_special_tokens=True, 
                                    clean_up_tokenization_spaces=False)[0].split('[/INST]')[-1].strip()
        return response
    
    def chat(self, prompt, ID, proxy='batch', temperature=0.0):
        with torch.no_grad():
            input_ids = self.encode('<s>')
            for msg in prompt:
                        if msg['role'] == 'user':
                            input_ids = torch.concat([input_ids, 
                                                        self.encode("[INST]"), 
                                                        self.encode(msg['content'].strip()), 
                                                        self.encode("[/INST]")], dim=-1)
                        else:
                            input_ids = torch.concat([input_ids,
                                                        self.encode(msg['content'].strip()),
                                                        self.encode('</s>')], dim=-1)
            response = None
            if proxy == 'stream':
                output_ids = self.generate(input_ids, self.streamer, temperature)
            elif proxy == 'batch':
                output_ids = self.generate(input_ids, None, temperature)
            else:
                raise ValueError("proxy must be 'stream' or 'batch'")
            response = self.decode(output_ids)
            print(f"ID: {ID}:\tSuccessfully made request")
        return response
    
    def ppl(self, input, output): 
        with torch.no_grad():
            input_ids = torch.concat([self.encode('<s>'), 
                                        self.encode("[INST]"),
                                        self.encode(input.strip()), 
                                        self.encode("[/INST]")], dim=-1)
            output_ids = torch.concat([self.encode(output.strip()),
                                        self.encode('</s>')], dim=-1)
            ids = torch.concat([input_ids, output_ids], dim=-1)
            labels = torch.full_like(ids, -100)
            labels[:, -output_ids.size(1):] = output_ids
            ppl = self.model(ids, labels=labels).loss.item()
            total_ppl = self.model(ids, labels=ids).loss.item()

        return ppl, total_ppl