import tiktoken
import pandas as pd
from PromptFormatter_Defects4J import EXAMPLE_INPUT_FUNC_AGENT, AGENT_PROMPT

input_per_price = 0.00001
output_per_price = 0.00003
sampling_number = 10

print(f"Price ($) per bug fix. Each bug sampling number is {sampling_number}.")

def count_tokens(text, model_name='gpt-4'):
    encoding = tiktoken.encoding_for_model(model_name)
    tokens = encoding.encode(str(text))
    return len(tokens)

# defects4j
df_bugfix = pd.read_csv('result/defects4j/results_agent_1shot_gpt-4_10try_temp=1.0_archived.csv', sep=',', encoding='utf-8')
df_bugfix['input_tokens'] = df_bugfix['bug'].apply(lambda x: count_tokens(x, 'gpt-4'))
fixed_bug_slug_ids = df_bugfix['slug'].tolist()
input_token_mean = df_bugfix['input_tokens'].mean()
df_bugfix['output_tokens'] = df_bugfix['fix'].apply(lambda x: count_tokens(x, 'gpt-4'))
output_token_mean = df_bugfix['output_tokens'].mean()
df_artifact = pd.read_csv('data/exceptions.csv', sep=',', encoding='utf-8')
df_artifact = df_artifact[df_artifact['slug'].isin(fixed_bug_slug_ids)]
df_artifact['test_method_tokens'] = df_artifact['test_method'].apply(lambda x: count_tokens(x, 'gpt-4'))
test_method_token_mean = df_artifact['test_method_tokens'].mean()
df_artifact['exception_info_tokens'] = df_artifact['exception_info'].apply(lambda x: count_tokens(x, 'gpt-4'))
test_method_token_mean = df_artifact['exception_info_tokens'].mean()
df_raw = pd.read_csv('data/eval.csv', sep=',', encoding='utf-8')
df_raw = df_raw[df_raw['slug'].isin(fixed_bug_slug_ids)]
df_raw['comment_tokens'] = df_raw['comment'].apply(lambda x: count_tokens(x, 'gpt-4'))
comment_token_mean = df_raw['comment_tokens'].mean()
input_mean = input_token_mean + test_method_token_mean + comment_token_mean + count_tokens(EXAMPLE_INPUT_FUNC_AGENT, 'gpt-4') + count_tokens(AGENT_PROMPT.replace('{BUGGY_COMMENT}','').replace('{ERROR_MESSAGE}','').replace('{FAILED_TEST}','').replace('{BUGGY_CODE}',''), 'gpt-4')
input_price = input_mean * input_per_price * sampling_number
print(f"input token mean: {input_mean}, input context price mean: {input_price}")
output_price = output_token_mean * output_per_price * sampling_number
print(f"output token mean: {output_token_mean}, output context price mean: {output_price}")
print(f"total bug-fix price mean: {input_price + output_price}")