from RemoteChatAgent import RemoteChatAgent
from LocalChatAgent import LocalChatAgent
from PromptFormatter import PromptFormatter
import argparse
from loguru import logger

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_key', default="sh-xxxx", type=str)
    parser.add_argument('--bug_id', default="Cli_3", type=str)
    parser.add_argument('--model_name', default="gpt-4", type=str)
    parser.add_argument('--agent', default="remote", type=str)
    
    parser.add_argument('--func_path', default="data/lined_data_v6.csv", type=str)
    parser.add_argument('--test_path', default="data/error_message_all.csv", type=str)
    parser.add_argument('--history_path', default="debug_history_plus.json", type=str)
    parser.add_argument('--log_path', default="data/demo.log", type=str)
    parser.add_argument('--model_dir', default="..", type=str)
    parser.add_argument('--proxy', default='AI', type=str)
    args = parser.parse_args()
    logger.add(args.log_path)

    if args.agent == 'local':
        chat_agent = LocalChatAgent(args.model_dir, args.model_name, args.history_path, logger)
    elif args.agent == 'remote':
        chat_agent = RemoteChatAgent(args.api_key, args.model_name, args.history_path, logger)
    else:
        raise ValueError("agent must be 'local' or 'remote'")
    prompt_formatter = PromptFormatter(args.func_path, args.test_path)

    ID, data = prompt_formatter.get_one_data(args.bug_id)
    prompt = prompt_formatter.format_prompt(**data)
    logger.info(f"Prompt: {prompt}")
    response = chat_agent.chat(prompt, ID, proxy=args.proxy)
    logger.info(f"Response: {response}")
