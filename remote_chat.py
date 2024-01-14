import subprocess
import json
import requests
import pandas as pd
import csv
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("debug.log"),
                        logging.StreamHandler()
                    ])

# Initialize dictionaries
buggy_methods_dict = {}
error_messages_dict = {}

# 1. Preprocess the buggy method data
buggy_method_path = 'lined_data_v5.csv'
with open(buggy_method_path, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter='¥')
    next(reader)  # Skip the header
    for row in reader:
        ID, comment, source_method, replaced_method = row[:4]
        if ID not in buggy_methods_dict:
            buggy_methods_dict[ID] = []
        buggy_methods_dict[ID].append({'Comment': comment, 'Source Method': source_method, 'Replaced Method': replaced_method})

# 2. Preprocess the error message data
error_message_examples_file_path = 'error_message_examples.csv'
with open(error_message_examples_file_path, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter='¥')
    next(reader)  # Skip the header
    for row in reader:
        ID, path, test_method_name, test_method, exception_info = row[:5]
        if ID not in error_messages_dict:
            error_messages_dict[ID] = []
        error_messages_dict[ID].append({'Path': path, 'Test Method Name': test_method_name, 'Test Method': test_method, 'Exception Info': exception_info})

# 3. Merge and output the data to JSON
combined_data = {}
for ID in set(buggy_methods_dict).union(error_messages_dict):
    combined_data[ID] = [data for data in buggy_methods_dict.get(ID, [])]
    combined_data[ID].extend(error_messages_dict.get(ID, []))

output_json_path = 'merged_data.json'
with open(output_json_path, 'w', encoding='utf-8') as json_file:
    json.dump(combined_data, json_file, ensure_ascii=False, indent=4)


# 3. LLM part
# Choose model: gpt-3.5-turbo, gpt-4, claude-2, palm-2-chat-bison, gemini-pro
model_name = "gpt-4"

with open("config.json", "r") as config_file:
    config_data = json.load(config_file)

# Get the api_key from the config data
api_key = config_data.get("api_key", "")

# logging.info("api_key:", api_key)

# Import chat history
with open("chat_history.json", "r", encoding='utf-8') as history_file:
    history_data = json.load(history_file)

with open('merged_data.json', 'r', encoding='utf-8') as file:
    merged_data = json.load(file)

# for ID, metadata in list(data.items())[:1]:
#     logging.info('ID: %s, Metadata: %s', ID, metadata)

# Iterate through each ID and construct the prompt
for ID, metadata in merged_data.items():
    if ID != 'Chart_1':
        continue
    logging.info('Processing ID: %s', ID)
    comments = []
    source_methods = []
    test_methods = []
    exception_infos = []

    # Aggregate metadata
    for entry in metadata:
        if 'Comment' in entry and 'Source Method' in entry:
            comments.append(entry['Comment'])
            source_methods.append(entry['Source Method'])
        if 'Test Method' in entry and 'Exception Info' in entry:
            test_methods.append(entry['Test Method'])
            exception_infos.append(entry['Exception Info'])

    # Combine all the information into a single prompt
    # prompt = f"ID: {ID}\n"
    prompt = f""
    for i in range(max(len(comments), len(test_methods))):
        prompt += "Next, you need to analyze the following code snippet.\n"
        prompt += f"Comment:\n{comments[i] if i < len(comments) else 'null'}\n"
        prompt += f"Source Method:\n{source_methods[i] if i < len(source_methods) else 'null'}\n"
        prompt += f"Test Method from JUnit:\n{test_methods[i] if i < len(test_methods) else 'null'}\n"
        prompt += f"Exception Info:\n{exception_infos[i] if i < len(exception_infos) else 'null'}\n"
        prompt += f"Carefully analyze this program for potential bugs following the example and error message provided. You should think step by step following the previous three questions. If there is a bug, output the buggy line number in format `<lineA>; <lineB>; <lineC>...` WITHOUT buggy code, and then propose a fix in markdown format ```java <YOUR FIX> ```, following the same format as previous examples. DO NOT show me the complete function. If there is no bug, ONLY output \"No bug\".\n\n"


    logging.info(prompt)
    new_message_user = {
        "role": "user",
        "content": prompt
    }
    history_data.append(new_message_user)

    data = {
        'model': model_name,
        'messages': history_data
    }

    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    response = requests.post(
        'https://aigptx.top/v1/chat/completions', json=data, headers=headers)

    if response.status_code != 200:
        logging.error(f"Error making request: {response.text}")
    else:
        logging.info("Successfully made request")
        response_data = response.json()

        # Append the new response to the chat history
        new_message_assistant = {
            "role": "assistant",
            "content": response_data['choices'][0]['message']['content']
        }
        history_data.append(new_message_assistant)

        # Save the updated history back to the file
        # with open("chat_history.json", "w", encoding='utf-8') as output_file:
        #     json.dump(history_data, output_file, ensure_ascii=False, indent=4)

        response_content = response_data['choices'][0]['message']['content']
        logging.info(response_content)

        fix_patch_pattern = r"```java\n(<line\d+>.*?)(?=\n```)"
        matches = re.findall(fix_patch_pattern, response_content, re.DOTALL)

        if matches:
            for match in matches:
                line_number_pattern = r"<line(\d+)>"
                line_numbers = re.findall(line_number_pattern, match)
                code_snippet = re.sub(line_number_pattern, "", match)

                logging.info("Extracted Line Numbers: %s", line_numbers)
                logging.info("Extracted Code Snippet: %s", code_snippet)
        else:
            logging.info("No fix patch found in LLM response.")
