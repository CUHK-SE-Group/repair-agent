api_key='sk-xxx'
model='gpt-4'
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
python debugbench_test_G\&V.py --mode agent --ablation comment --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature
python debugbench_test_G\&V.py --mode agent --ablation example  --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature
python debugbench_test_G\&V.py --mode agent --ablation message --api_key $api_key --remote_model $model --max_try $max_try --temperature $temperature
