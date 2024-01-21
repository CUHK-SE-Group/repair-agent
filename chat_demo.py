from RemoteChatAgent import RemoteChatAgent
from PromptFormatter import PromptFormatter
import argparse
from loguru import logger

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_key', type=str, required=True)
    parser.add_argument('--bug_id', default="Cli_3", type=str)
    parser.add_argument('--model_name', default="gpt-4", type=str) # Choose model: gpt-3.5-turbo, gpt-4, claude-2, palm-2-chat-bison, gemini-pro
    
    parser.add_argument('--func_path', default="data/lined_data_v6.csv", type=str)
    parser.add_argument('--test_path', default="data/error_message_all.csv", type=str)
    parser.add_argument('--history_path', default="debug_history_refined.json", type=str)
    parser.add_argument('--log_path', default="data/remote_chat_demo.log", type=str)
    parser.add_argument('--proxy', default='AI', type=str)
    args = parser.parse_args()
    logger.add(args.log_path)

    remote_chat_agent = RemoteChatAgent(args.api_key, args.model_name, args.history_path, logger)
    prompt_formatter = PromptFormatter(args.func_path, args.test_path)

    ID, data = prompt_formatter.get_one_data(args.bug_id)
    prompt = prompt_formatter.format_prompt(**data)
    logger.info(f"Prompt: {prompt}")
    response = remote_chat_agent.chat(prompt, ID, proxy=args.proxy)
    logger.info(f"Response: {response}")

    ### Need verify response
