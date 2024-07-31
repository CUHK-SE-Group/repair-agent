# ///////////////////////////////////////////////////////////////////////////////#
# NOTE: The following setting is for remote model (GPT-4)                        #
# If you want to use local model (Mixtral),                                      #
# you should delete `--api_key` argument,                                        #
# change `--remote_model` argument to `--local_model`,                           #
# change `model='gpt-4-0613'` to `model='mixtral-8x7b-instruct'`,                     #
# and add `--chat_mode local` argument to the following commands.                #
# Before using Mixtral,                                                          #
# you should download the model from Hugging Face and place it in this directory.#
# ///////////////////////////////////////////////////////////////////////////////#

# Settings
api_key='sk-xxx'
model='gpt-4-0613'
max_try=10
temperature=1.0

# RQ1
python defects4j_test_G\&V.py --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature

# RQ2
python debugbench_test_G\&V.py --mode agent --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature
python debugbench_test_G\&V.py --mode hybrid --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature
python debugbench_test_G\&V.py --mode reverse --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature
python debugbench_test_G\&V.py --mode located --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature

# RQ3
python defects4j_test_G\&V.py --ablation comment --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature
python defects4j_test_G\&V.py --ablation example --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature
python defects4j_test_G\&V.py --ablation message --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature
python defects4j_test_G\&V.py --mode pure --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature
python debugbench_test_G\&V.py --mode agent --ablation comment --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature
python debugbench_test_G\&V.py --mode agent --ablation example  --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature
python debugbench_test_G\&V.py --mode agent --ablation message --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature
python debugbench_test_G\&V.py --mode pure --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature
