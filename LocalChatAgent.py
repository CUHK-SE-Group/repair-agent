from transformers import AutoModelForCausalLM, AutoTokenizer

model_path = "mixtral-7bx8moe-instruct"

model =  AutoModelForCausalLM.from_pretrained(model_path, device_map='auto', low_cpu_mem_usage=True)
tokenizer = AutoTokenizer.from_pretrained(model_path)
prompt = '<s>'
instruction = input("<|User|>: ")
while instruction:
        prompt = prompt + "[INST] " + instruction.strip() + " [/INST]"
        input_ids = tokenizer(prompt, 
                              return_tensors="pt", 
                              add_special_tokens=False
                              ).input_ids.cuda()
        output_ids = model.generate(input_ids, 
                                  max_new_tokens=2048, 
                                  do_sample = True, 
                                  top_k = 30, 
                                  top_p = 0.85, 
                                  temperature = 0.5, 
                                  repetition_penalty=1.,
                                  pad_token_id = tokenizer.eos_token_id,) # for open-end generation
        rets = tokenizer.batch_decode(output_ids, 
                                      skip_special_tokens=False, 
                                      clean_up_tokenization_spaces=False) 
        response = rets[0].split('[/INST]')[-1].split('</s>')[0].strip()
        prompt = prompt + response + '</s>'
        print("<|Assisstant|>: " + response)
        # print("<|History|>: " + prompt) # the complete dialogue history
        print("--------------------------------------------------------------")
        instruction = input("<|User|>: ")