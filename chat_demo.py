from RemoteChatAgent import RemoteChatAgent
from PromptFormatter import PromptFormatter
import argparse
from loguru import logger

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_key', type=str, required=True)
    parser.add_argument('--model_name', default="gpt-3.5-turbo", type=str) # Choose model: gpt-3.5-turbo, gpt-4, claude-2, palm-2-chat-bison, gemini-pro
    args = parser.parse_args()

    function_context_file_path = 'data/lined_data_v5.csv'
    error_message_file_path = 'data/error_message_examples.csv'
    chat_history_file_path = 'chat_history.json'
    logger.add("data/remote_chat.log")

    remote_chat_agent = RemoteChatAgent(args.api_key, args.model_name, chat_history_file_path, logger)
    prompt_formatter = PromptFormatter(function_context_file_path, error_message_file_path)

    ID, data = prompt_formatter.get_one_data(0)
    prompt = prompt_formatter.format_prompt(**data)
    logger.info(f"Prompt: {prompt}")
    response = remote_chat_agent.chat(prompt, ID)
    logger.info(f"Response: {response}")