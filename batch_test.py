from RemoteChatAgent import RemoteChatAgent
from LocalChatAgent import LocalChatAgent
from PromptFormatter import PromptFormatter
import argparse
from loguru import logger
import pandas as pd
import random

random.seed(42)

proj_list = ['Chart',
            'Math',
            'Lang',
            'Cli',
            'Closure',
            'Codec',
            'Mockito',
            'Jsoup',
            'JacksonDatabind',
            'JacksonCore',
            'Compress',
            'Collections',
            'Time',
            'JacksonXml',
            'Gson',
            'Csv',
            'JxPath']   
id_range = ['1-25',
            '1-105',
            '1-64',
            '2-40',
            '1-170',
            '2-18',
            '1-37',
            '2-93',
            '2-112',
            '2-26',
            '2-47',
            '26-28',
            '1-27',
            '2-6',
            '2-18',
            '2-16',
            '2-22',]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_key', default="sh-xxxx", type=str)
    parser.add_argument('--model_name', default="gpt-4", type=str) # Choose model: gpt-3.5-turbo, gpt-4, claude-2, palm-2-chat-bison, gemini-pro
    parser.add_argument('--num_bugs', default=20, type=int)
    parser.add_argument('--num_patches', default=10, type=int)
    parser.add_argument('--agent', default="remote", type=str)
    
    parser.add_argument('--func_path', default="data/lined_data_v6.csv", type=str)
    parser.add_argument('--test_path', default="data/error_message_all.csv", type=str)
    parser.add_argument('--history_path', default="debug_history_plus.json", type=str)
    parser.add_argument('--log_path', default="data/batch.log", type=str)
    parser.add_argument('--results_path', default="data/results.csv", type=str)
    parser.add_argument('--model_dir', default="..", type=str)
    parser.add_argument('--proxy', default='AI', type=str)
    args = parser.parse_args()
    logger.add(args.log_path)

    if args.agent == 'local':
        chat_agent = LocalChatAgent(args.model_dir, args.model_name, args.history_path, logger)
    elif args.agent == 'remote':
        chat_agent = RemoteChatAgent(args.api_key, args.model_name, args.history_path, logger)
    prompt_formatter = PromptFormatter(args.func_path, args.test_path)

    df_results = pd.DataFrame(columns=['ID', 'Bug Report', 'Patch Solutions'])
    df_IDlist = pd.read_csv(args.func_path, sep='¥', engine='python')['ID']
    id_count = df_IDlist.value_counts()

    for i in range(args.num_bugs):
        while True:
            proj_idx = random.randint(0, len(proj_list)-1)
            start_idx, end_idx = id_range[proj_idx].split('-')
            id = random.randint(int(start_idx), int(end_idx)-1)
            bug_id = proj_list[proj_idx] + '_' + str(id)
            if bug_id not in df_results['ID'] and bug_id in id_count and id_count[bug_id] == 1: # avoid bugs with multiple functions
                break
        logger.info(f"Generating BugID: {bug_id} ...") 
        ID, data = prompt_formatter.get_one_data(bug_id)
        prompt = prompt_formatter.format_prompt(**data)       
        for j in range(args.num_patches):
            logger.info(f"Generating Patch {j+1} for BugID: {bug_id} ...")
            response = chat_agent.chat(prompt, ID, proxy=args.proxy)
            df_results.loc[i * args.num_patches + j] = {'ID': bug_id, 'Bug Report': prompt, 'Patch Solutions': response}
            df_results.to_csv(args.results_path, sep='¥', encoding='utf-8')
