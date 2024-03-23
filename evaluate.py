from LocalChatter import LocalChatter
from PromptFormatter_Defects4J import *
from JUnitVerifier import *
from PatchMerger import *
import pandas as pd
import json


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


def ppl_evaluate(results, data, result_path, ppl_path, df_ppl):
    debugger = LocalChatter("../", "mixtral-8x7b-instruct")
    for i, row in results.iterrows():
        sample = data[i]
        if 'agent' in result_path or 'reverse' in result_path:
            prompt = AGENT_PROMPT
            prompt = prompt.replace("{LANGUAGE}", sample['language'].strip())
            prompt = prompt.replace("{REQUIREMENT}", sample['question'].strip())
            prompt = prompt.replace("{CONSTRAINT}", sample['constraints'].strip())
            prompt = prompt.replace("{EXAMPLE}", '\n'.join(sample['examples']).strip())
            if 'agent' in result_path: # different output
                prompt = prompt.replace("{BUGGY_CODE}", sample['buggy_code'].strip())
                prompt = prompt.strip() + "\nPlease follow your duty as an AI Debugger and generate a refined version of the buggy program."
                response = f"```{sample['language']}\n" + row['fix'].strip() + "\n```"
            else:
                prompt = prompt.replace("{BUGGY_CODE}", sample['located_code'].strip())
                prompt = prompt.strip() + "\nPlease follow your duty as an AI Debugger and generate the corrected code snippets for the buggy program."
                response = f"```{sample['language']}\n" + row['diff'].strip() + "\n```"
        elif 'located' in result_path or 'hybrid' in result_path:
            prompt = USER_PROMPT
            prompt = prompt.replace("{LANGUAGE}", sample['language'].strip())
            if 'located' in result_path:
                prompt = prompt.replace("{BUGGY_CODE}", sample['located_code'].strip())
                prompt = prompt.strip() + "\nPlease follow your duty as an AI Debugger and generate code snippets to fill the chunks marked as `<Chunk_For_Modification>` in each provided buggy function."
                response = f"```{sample['language']}\n" + row['diff'].strip() + "\n```"
            else:
                prompt = prompt.replace("{BUGGY_CODE}", sample['buggy_code'].strip())
                prompt = prompt.strip() + "\nPlease follow your duty as an AI Debugger and generate a refined version of the buggy program."
                response = f"```{sample['language']}\n" + row['fix'].strip() + "\n```" 
        # print(prompt)
        # print(response)
        # break
        try:
            ppl, total_ppl = debugger.ppl(prompt, response)
        except Exception as e:
            ppl = "OOM"
            total_ppl = "OOM"
        df_ppl.loc[i] = {'ID': i, 'slug': sample['slug'], 'ppl': ppl, 'total_ppl': total_ppl}
        df_ppl.to_csv(ppl_path, sep=',', encoding='utf-8', index=False)


def junit_evaluate(results, eval_path, df_eval, data):
    for i, row in results.iterrows():
        bug_slug = row['slug']
        sample = data[data['slug'] == bug_slug].iloc[0]
        reward, submission_result = verify(row['slug'], sample['class_path'], sample['buggy_code'], row['fix'])
        df_eval.loc[i] = {'ID': i, 'slug': sample['slug'], 'reward': reward, 'submission_result': submission_result}
        df_eval.to_csv(eval_path, sep=',', encoding='utf-8', index=False)


def calculate_pass(eval_path):
    evaluation = pd.read_csv(eval_path, sep=',', encoding='utf-8', engine='python')
    name_list = ['Chart', 'Lang', 'Math', 'Mockito', 'Time']
    total_list = []
    pass_list = []
    sp_list = []
    for i, row in evaluation.iterrows():
        total_list.append(row['slug'])
        if row['reward'] == True and row['slug'] not in pass_list:
            pass_list.append(row['slug'])
            if row['slug'] not in sp_list and row['slug'].split('_')[0] in name_list:
                sp_list.append(row['slug'])
            if row['slug'] not in sp_list and row['slug'].split('_')[0] == 'Closure' and int(row['slug'].split('_')[1]) <= 133:
                sp_list.append(row['slug'])
    print(f"Pass: {len(pass_list)}")
    print(f"Pass-1.2: {len(sp_list)}")
    # print(sp_list)

def calculate_ppl(ppl_path):
    evaluation = pd.read_csv(ppl_path, sep=',', encoding='utf-8', engine='python')
    total_ppl = 0
    total_total_ppl = 0
    for i, row in evaluation.iterrows():
        if row['ppl'] != 'OOM':
            total_ppl += float(row['ppl'])
            total_total_ppl += float(row['total_ppl'])
    print(f"Average PPL: {total_ppl / len(evaluation)}")
    print(f"Average Total PPL: {total_total_ppl / len(evaluation)}")


def calculate_sample1(eval_path):
    evaluation = pd.read_csv(eval_path, sep=',', encoding='utf-8', engine='python')
    total_list = []
    pass_list = []
    for i, row in evaluation.iterrows():
        if row['slug'] not in total_list:
            total_list.append(row['slug'])
            if row['reward'] == True:
                pass_list.append(row['slug'])
    print(f"Pass: {len(pass_list)}")


def calculate_sample3(eval_path):
    evaluation = pd.read_csv(eval_path, sep=',', encoding='utf-8', engine='python')
    total_list = []
    pass_list = []
    for i, row in evaluation.iterrows():
        if total_list.count(row['slug']) < 3:
            total_list.append(row['slug'])
            if row['reward'] == True and row['slug'] not in pass_list:
                pass_list.append(row['slug'])
    print(f"Pass: {len(pass_list)}")


def calculate_sample1_pl3(eval_path):
    evaluation = pd.read_csv(eval_path, sep=',', encoding='utf-8', engine='python')
    total_list_cpp = []
    total_list_java = []
    total_list_python = []
    pass_list_cpp = []
    pass_list_java = []
    pass_list_python = [] 
    for i, row in evaluation.iterrows():
        if "'lang': 'cpp'" in row['submission_result']:
            if row['slug'] not in total_list_cpp:
                total_list_cpp.append(row['slug'])
                if row['reward'] == True:
                    pass_list_cpp.append(row['slug'])
        if "'lang': 'java'" in row['submission_result']:
            if row['slug'] not in total_list_java:
                total_list_java.append(row['slug'])
                if row['reward'] == True:
                    pass_list_java.append(row['slug'])
        if "'lang': 'python3'" in row['submission_result']:
            if row['slug'] not in total_list_python:
                total_list_python.append(row['slug'])
                if row['reward'] == True:
                    pass_list_python.append(row['slug'])
    print(f"Pass cpp: {len(pass_list_cpp)}")
    print(f"Pass java: {len(pass_list_java)}")
    print(f"Pass python: {len(pass_list_python)}")


if __name__ == '__main__':
    data_path = "data/lined_data2.csv"
    msg_path =  "data/error_message2.csv"
    eval_path = "result/defects4j/evaluation_comment_1shot_gpt-4_10try_temp=1.0.csv"
    # ppl_evaluate()
    # junit_evaluate()
    calculate_pass(eval_path)
    # calculate_ppl()
    # calculate_sample1()
    # calculate_sample3()
    # calculate_sample1_pl3()