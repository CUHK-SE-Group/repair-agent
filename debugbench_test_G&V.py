from LocalChatter import LocalChatter
from RemoteChatter import RemoteChatter
from PromptFormatter_DebugBench import *
from LeetcodeVerifier import *
from PatchMerger import *
import argparse
import pandas as pd
import json
import time
from datetime import datetime
from tqdm import tqdm
import csv
csv.field_size_limit(10000000)


def debug(args):
    json_file = open(args.data_path, 'r')
    data = json.load(json_file)
    json_file.close()
    row_num = 0
    if os.path.exists(args.result_path):
        df_results = pd.read_csv(args.result_path, sep=',', encoding='utf-8', engine='python')
        row_num = df_results['ID'].iloc[-1]
    else:
        df_results = pd.DataFrame(columns=['ID', 'lang', 'slug', 'bug', 'diff', 'fix'])
    print(f'start from {row_num}')


    if args.mode == 'agent':
        history_list = HISTORY_AGENT_LIST
    elif args.mode == 'located':
        history_list = HISTORY_LOCATED_LIST
    elif args.mode == 'hybrid':
        history_list = HISTORY_HYBRID_LIST
    elif args.mode == 'reverse':
        history_list = HISTORY_REVERSE_LIST


    if args.chat_mode == 'remote':
        debugger = RemoteChatter(args.api_key, args.remote_model)
    elif args.chat_mode == 'local':
        debugger = LocalChatter(args.model_dir, args.local_model)
    else:
        raise ValueError("chat_mode must be 'remote' or 'local'")
    
    count = 0 
    for i in range(len(data)): # range from 37 to 91
        sample = data[i]

        if i < row_num:
            continue


        # if sample['slug'] != 'buddy-strings':
        #     continue


        if sample['category'] != "logic error":
            continue


        # if sample['language'] != "python3":
        #     continue

        # count += 1
        # if count > 5:
        #     break

        prompt = history_list[sample['language']] # select languange specific history
        prompt = prompt.copy()


        # different input
        if args.mode == 'agent' or args.mode == 'reverse':
            query = AGENT_PROMPT
            query = query.replace("{LANGUAGE}", sample['language'].strip())
            query = query.replace("{REQUIREMENT}", sample['question'].strip())
            query = query.replace("{CONSTRAINT}", sample['constraints'].strip())
            query = query.replace("{EXAMPLE}", '\n'.join(sample['examples']).strip())
            if args.mode == 'agent': # different output
                query = query.replace("{BUGGY_CODE}", sample['buggy_code'].strip())
                query = query.strip() + "\nPlease follow your duty as an AI Debugger and generate a refined version of the buggy program."
            else:
                query = query.replace("{BUGGY_CODE}", sample['located_code'].strip())
                query = query.strip() + "\nPlease follow your duty as an AI Debugger and generate the corrected code snippets for the buggy program."
        elif args.mode == 'located' or args.mode == 'hybrid':
            query = USER_PROMPT
            query = query.replace("{LANGUAGE}", sample['language'].strip())
            if args.mode == 'located':
                query = query.replace("{BUGGY_CODE}", sample['located_code'].strip())
                query = query.strip() + "\nPlease follow your duty as an AI Debugger and generate code snippets to fill the chunks marked as `<Chunk_For_Modification>` in each provided buggy function."
            else:
                query = query.replace("{BUGGY_CODE}", sample['buggy_code'].strip())
                query = query.strip() + "\nPlease follow your duty as an AI Debugger and generate a refined version of the buggy program."
        else:
            raise ValueError("mode must be 'located' or 'hybrid' or 'reverse' or 'agent'")

        prompt.append({
            "role": "user",
            "content": query
        })


        if args.ablation != 'full':
            if args.ablation == 'comment':
                pattern = r'### Program requirements:\n```[\s\S]*?```\n\n'
            elif args.ablation == 'example':
                pattern = r'### Test examples:\n```[\s\S]*?```\n\n'
            elif args.ablation == 'message':
                pattern = r'### Input constraints:\n```[\s\S]*?```\n\n'
            else:
                raise ValueError("ablation must be 'full' or 'comment' or 'case' or 'message'")
            prompt[1]['content'] = re.sub(pattern, '', prompt[1]['content'])
            prompt[3]['content'] = re.sub(pattern, '', prompt[3]['content'])


        for j in range(args.max_try):
            try:
                if args.mode in {'agent', 'hybrid'}:
                    response = debugger.chat(prompt, i, args.proxy, temperature=args.temperature)
                    fixed_code = extract_code(response)[0]
                    df_results.loc[i * args.max_try + j] = {'ID': i, 'lang': sample['language'], 'slug': sample['slug'], 'bug': sample['buggy_code'], 'diff': 'None', 'fix': fixed_code}
                    df_results.to_csv(args.result_path, sep=',', encoding='utf-8', index=False)
                    
                elif args.mode in {'located', 'reverse'}:
                    response = debugger.chat(prompt, i, args.proxy, temperature=args.temperature)
                    codeblock = extract_code(response)
                    if len(codeblock) == sample['located_code'].count('<Chunk_For_Modification>'):
                        fixed_code = sample['located_code']
                        patch = '\n'.join(codeblock)
                        for hunk in codeblock:
                            fixed_code = fixed_code.replace('<Chunk_For_Modification>', hunk, 1)
                        df_results.loc[i * args.max_try + j] = {'ID': i, 'lang': sample['language'], 'slug': sample['slug'], 'bug': sample['located_code'], 'diff': patch, 'fix': fixed_code}
                        df_results.to_csv(args.result_path, sep=',', encoding='utf-8', index=False)
                    elif args.mode == 'reverse':
                        patch = '\n'.join(codeblock)
                        df_results.loc[i * args.max_try + j] = {'ID': i, 'lang': sample['language'], 'slug': sample['slug'], 'bug': sample['located_code'], 'diff': patch, 'fix': 'To Be Applied'}
                        df_results.to_csv(args.result_path, sep=',', encoding='utf-8', index=False)
                    else:
                        df_results.loc[i * args.max_try + j] = {'ID': i, 'lang': sample['language'], 'slug': sample['slug'], 'bug': sample['located_code'], 'diff': 'None', 'fix': 'Match failed'}
                        df_results.to_csv(args.result_path, sep=',', encoding='utf-8', index=False)

                # for item in prompt:
                #     print(item['content'])
                #     print('-'*80)
                # print(fixed_code)
                # exit()
                        
            except Exception as e:
                print(e)


def merge(args):
    data = pd.read_csv(args.result_path, sep=',', encoding='utf-8', engine='python')
    data_merged = data.copy()
    if args.chat_mode == 'remote':
        debugger = RemoteChatter(args.api_key, args.remote_model)
    elif args.chat_mode == 'local':
        debugger = LocalChatter(args.model_dir, args.local_model)
    else:
        raise ValueError("chat_mode must be 'remote' or 'local'")
    history_list = HISTORY_MERGE_LIST
    for idx, row in data.iterrows():
        prompt = history_list[row['lang']]
        prompt = prompt.copy()
        query = MERGE_PROMPT
        query = query.replace("{LANGUAGE}", row['lang'])
        query = query.replace("{PATCH}", row['diff'])
        query = query.replace("{SOURCE}", row['bug'])
        prompt.append({
            "role": "user",
            "content": query
        })
        # for item in prompt:
        #     print(item['content'])
        #     print('-'*80)
        # exit()
        response = debugger.chat(prompt, idx, args.proxy, temperature=args.temperature)
        fixed_code = extract_code(response)[0]
        data_merged.at[idx, 'fix'] = fixed_code
        data_merged.to_csv(args.result_path, sep=',', encoding='utf-8', index=False)
    data.to_csv(args.result_path.replace(".csv", "_merged.csv"), sep=',', encoding='utf-8', index=False)


def verify(args):
    data = pd.read_csv(args.result_path, sep=',', encoding='utf-8', engine='python')
    print(data)
    row_num = 0
    if os.path.exists(args.eval_path):
        df_results = pd.read_csv(args.eval_path, sep=',', encoding='utf-8', engine='python')
        row_num = df_results.shape[0]
    else:
        df_results = pd.DataFrame(columns=['ID', 'slug', 'reward', 'submission_result'])
    print(f'start from {row_num}')

    tester = LeetcodeVerifier(0) # single cookie

    last_correct_slug = ""
    last_correct_info = ""
    iter_test = 0
    last_run = datetime.now()
    for idx, row in tqdm(data.iterrows()):

        if idx < row_num:
            continue
        if row['fix'] == 'Match failed':
            continue
        
        if row['slug'] == last_correct_slug:
            reward = True
            submission_result = last_correct_info
        else:

            ### loop cookies
            while (datetime.now() - last_run).total_seconds() < 10:
                time.sleep(0.1)
            tester = LeetcodeVerifier(iter_test)
            last_run = datetime.now()

            reward, submission_result = tester.test(row['fix'], row['slug'], row['lang'])
            iter_test += 1
            if reward:
                last_correct_slug = row['slug']
                last_correct_info = submission_result
        df_results.loc[idx] = {'ID': row['ID'], 'slug': row['slug'], 'reward': reward, 'submission_result': submission_result}
        df_results.to_csv(args.eval_path, sep=',', encoding='utf-8', index=False)


def evaluate(args):
    data = pd.read_csv(args.eval_path, sep=',', encoding='utf-8', engine='python')
    correct_list_cpp, correct_list_java, correct_list_python3 = [], [], []
    for i, row in data.iterrows():
        if row['reward'] == True:
            if row['slug'] not in correct_list_cpp and "'lang': 'cpp'" in row['submission_result']:
                correct_list_cpp.append(row['slug'])
            if row['slug'] not in correct_list_java and "'lang': 'java'" in row['submission_result']:
                correct_list_java.append(row['slug'])
            if row['slug'] not in correct_list_python3 and "'lang': 'python3'" in row['submission_result']:
                correct_list_python3.append(row['slug'])
    print(f"Pass cpp: {len(correct_list_cpp)}")
    print(f"Pass java: {len(correct_list_java)}")
    print(f"Pass python3: {len(correct_list_python3)}")
    print(f"Pass total: {len(correct_list_cpp) + len(correct_list_java) + len(correct_list_python3)}")
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_key', default="sh-xxxx", type=str)
    parser.add_argument('--model_dir', default="..", type=str)
    parser.add_argument('--chat_mode', default="remote", type=str) # remote or local
    parser.add_argument('--remote_model', default="gpt-4-0613", type=str) # Choose model: gpt-3.5-turbo, gpt-4, claude-2, palm-2-chat-bison, gemini-pro
    parser.add_argument('--local_model', default='mixtral-8x7b-instruct', type=str)
    parser.add_argument('--data_path', default="data/eval.json", type=str) 
    parser.add_argument('--result_path', default="result/debugbench/results", type=str)
    parser.add_argument('--eval_path', default="result/debugbench/evaluation", type=str)
    parser.add_argument('--proxy', default='OpenAI', type=str)
    parser.add_argument('--mode', default='agent', type=str)
    parser.add_argument('--shot', default=1, type=int)
    parser.add_argument('--max_try', default=3, type=int)
    parser.add_argument('--temperature', default=1.0, type=float)
    parser.add_argument('--ablation', default='full', type=str)
    args = parser.parse_args()

    result_elements = [args.result_path, args.mode, args.ablation, str(args.shot)]
    eval_elements = [args.eval_path, args.mode, args.ablation, str(args.shot)]

    if args.chat_mode == 'remote':
        args.result_path = '_'.join(elem for elem in result_elements if elem != '') + f'shot_{args.remote_model}_{args.max_try}try_temp={args.temperature}.csv'
        args.eval_path = '_'.join(elem for elem in eval_elements if elem != '') + f'shot_{args.remote_model}_{args.max_try}try_temp={args.temperature}.csv'
    elif args.chat_mode == 'local':
        args.result_path = '_'.join(elem for elem in result_elements if elem != '') + f'shot_{args.local_model}_{args.max_try}try_temp={args.temperature}.csv'
        args.eval_path = '_'.join(elem for elem in eval_elements if elem != '') + f'shot_{args.local_model}_{args.max_try}try_temp={args.temperature}.csv'
    else:
        raise ValueError("chat_mode must be 'remote' or 'local'")

    debug(args)
    verify(args)

    
            
        




