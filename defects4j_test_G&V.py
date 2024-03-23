from LocalChatter import LocalChatter
from RemoteChatter import RemoteChatter
from PromptFormatter_Defects4J import *
from JUnitVerifier import *
from PatchMerger import *
import argparse
import pandas as pd


def debug(args):
    data = pd.read_csv(args.data_path, sep=',', encoding='utf-8', engine='python')
    msg = pd.read_csv(args.msg_path, sep=',', encoding='utf-8', engine='python')
    id_count = data['slug'].value_counts()
    total_unique = id_count[id_count == 1].sum()
    print(f"total number of unique function bug: {total_unique}")
    # extract all the unique 'slug" data
    data = data.groupby('slug').filter(lambda x: len(x) == 1)
    row_num = 0
    if os.path.exists(args.result_path):
        df_results = pd.read_csv(args.result_path, sep=',', encoding='utf-8', engine='python')
        row_num = df_results['ID'].iloc[-1]
    else:
        df_results = pd.DataFrame(columns=['ID', 'lang', 'slug', 'bug', 'diff', 'fix'])
    if os.path.exists(args.eval_path):
        df_eval = pd.read_csv(args.eval_path, sep=',', encoding='utf-8', engine='python')
    else:
        df_eval = pd.DataFrame(columns=['ID', 'slug', 'reward', 'submission_result'])

    # for plausible check
    if args.ablation == 'full' and args.check:
        plausible_df = pd.read_csv('result/defects4j/evaluation_agent_1shot_gpt-4_10try_temp=1.0.csv', sep=',', encoding='utf-8', engine='python')
        reward_true_df = plausible_df[plausible_df['reward'] == True]
        slugs = set(reward_true_df['slug'])

    history = HISTORY_AGENT_D4J

    if args.chat_mode == 'remote':
        debugger = RemoteChatter(args.api_key, args.remote_model)
    elif args.chat_mode == 'local':
        debugger = LocalChatter(args.model_dir, args.local_model)
    else:
        raise ValueError("chat_mode must be 'remote' or 'local'")

    for i, row in data.iterrows():
        sample = row

        if i < row_num:
            continue

        if args.ablation == 'full' and args.check and sample['slug'] not in slugs:
            print(f"skip fault patch slugs: {sample['slug']}")
            continue

        # if i > 5: # end at xxx
        # if i <= 304: # start at xxx
            # continue
        

        prompt = history.copy()
        query = AGENT_PROMPT
        query = query.replace("{BUGGY_COMMENT}", sample['comment'].strip() if str(sample['comment']) not in {'', 'nan'} else "This function has no comment.")
        query = query.replace("{ERROR_MESSAGE}", msg[msg['slug'] == sample['slug']]['exception_info'].values[0] if len(msg[msg['slug'] == sample['slug']]['exception_info'].values) > 0 else "This function has no exception info.")
        query = query.replace("{FAILED_TEST}", msg[msg['slug'] == sample['slug']]['test_method'].values[0] if len(msg[msg['slug'] == sample['slug']]['test_method'].values) > 0 else "This function has no failed test.")
        query = query.replace("{BUGGY_CODE}", sample['buggy_code'].strip())
        
        prompt.append({
            "role": "user",
            "content": query
        })

        if args.ablation != 'full':
            if args.ablation == 'comment':
                pattern = r'### Buggy function comment:\n[\s\S]*?(?=\n###)'
            elif args.ablation == 'example':
                pattern = r'### Failed JUnit test:\n[\s\S]*?(?=\n###)'
            elif args.ablation == 'message':
                pattern = r'### Error message from JUnit test:\n[\s\S]*?(?=\n###)'
            else:
                raise ValueError("ablation must be 'full' or 'comment' or 'case' or 'message'")
            prompt[1]['content'] = re.sub(pattern, '', prompt[1]['content'])
            prompt[3]['content'] = re.sub(pattern, '', prompt[3]['content'])

        for j in range(args.max_try):
            try:
                response = debugger.chat(prompt, i, args.proxy, temperature=args.temperature)
                fixed_code = extract_code(response)[0]
                reward, submission_result = verify(sample['slug'], sample['class_path'], sample['buggy_code'], fixed_code)
                df_results.loc[i * args.max_try + j] = {'ID': i, 'lang': 'java', 'slug': sample['slug'], 'bug': sample['buggy_code'], 'diff': 'None', 'fix': fixed_code}
                df_results.to_csv(args.result_path, sep=',', encoding='utf-8', index=False)
                df_eval.loc[i * args.max_try + j] = {'ID': i, 'slug': sample['slug'], 'reward': reward, 'submission_result': submission_result}
                df_eval.to_csv(args.eval_path, sep=',', encoding='utf-8', index=False)
                if args.ablation != 'full' and reward:
                    break
                # for item in prompt:
                #     print(item['content'])
                #     print('-'*80)
                # print(fixed_code)
                # exit()    

            except Exception as e:
                print(e)  
                

# def merge(args):
#     data = pd.read_csv(args.result_path, sep=',', encoding='utf-8', engine='python')
#     for idx, row in data.iterrows():
#         try:
#             source = row['bug']
#             patch = extract_code(row['diff'])
#             fixed_code = apply_diff_to_program(source, patch)
#             data.at[idx, 'fix'] = fixed_code
#         except Exception as e:
#             print(f"{row['slug']}: {e}")
#     data.to_csv(args.result_path, sep=',', encoding='utf-8', index=False)


def verify(bug_id, class_path, original_method, fixed_method):
    if fixed_method == 'Match failed':
        return False, 'Match failed'
    bug_id = bug_id
    original_method = original_method.strip()
    original_method_len = len(original_method.split('\n'))
    fixed_method = fixed_method.replace('@Override', '').strip()
    function_head = fixed_method.split('{')[0].split(')')[0] + ')'
    function_head = function_head.strip()

    class_replace_index = extract_method_start_end_index(class_path, function_head, original_method_len)
    if class_replace_index is None:
        return False, 'Locate failed'
    replace_file(class_path, class_replace_index, fixed_method)
    reward, submission_result = run_JUnit(bug_id)
    restore_file(class_path, bug_id)
    return reward, submission_result

def evaluate(args):
    data = pd.read_csv(args.eval_path, sep=',', encoding='utf-8', engine='python')
    print(data['reward'].value_counts())
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_key', default="sh-xxxx", type=str)
    parser.add_argument('--model_dir', default="..", type=str)
    parser.add_argument('--chat_mode', default="remote", type=str) # remote or local
    parser.add_argument('--remote_model', default="gpt-4", type=str) # Choose model: gpt-3.5-turbo, gpt-4, claude-2, palm-2-chat-bison, gemini-pro
    parser.add_argument('--local_model', default='mixtral-8x7b-instruct', type=str)
    parser.add_argument('--data_path', default="data/eval.csv", type=str) 
    parser.add_argument('--msg_path', default="data/exceptions.csv", type=str)
    parser.add_argument('--result_path', default="result/defects4j/results", type=str)
    parser.add_argument('--eval_path', default="result/defects4j/evaluation", type=str)
    parser.add_argument('--proxy', default='AI', type=str)
    parser.add_argument('--shot', default=1, type=int)
    parser.add_argument('--max_try', default=10, type=int)
    parser.add_argument('--temperature', default=1.0, type=float)
    parser.add_argument('--ablation', default='full', type=str)
    parser.add_argument('--check', default=False, type=bool)
    args = parser.parse_args()

    result_elements = [args.result_path, args.ablation, str(args.shot)]
    eval_elements = [args.eval_path, args.ablation, str(args.shot)]

    if args.chat_mode == 'remote':
        args.result_path = '_'.join(elem for elem in result_elements if elem != '') + f'shot_{args.remote_model}_{args.max_try}try_temp={args.temperature}.csv'
        args.eval_path = '_'.join(elem for elem in eval_elements if elem != '') + f'shot_{args.remote_model}_{args.max_try}try_temp={args.temperature}.csv'
    elif args.chat_mode == 'local':
        args.result_path = '_'.join(elem for elem in result_elements if elem != '') + f'shot_{args.local_model}_{args.max_try}try_temp={args.temperature}.csv'
        args.eval_path = '_'.join(elem for elem in eval_elements if elem != '') + f'shot_{args.local_model}_{args.max_try}try_temp={args.temperature}.csv'
    else:
        raise ValueError("chat_mode must be 'remote' or 'local'")

    debug(args)
    # evaluate(args)
    # verify(args)

    
            
        




