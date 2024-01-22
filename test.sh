api_key=sk-xxxx # your api key

# demo
python chat_demo.py --agent remote --api_key $api_key --model_name gpt-4 --proxy OMG --log_path data/remote_demo.log # remote demo
python chat_demo.py --agent local --model_dir .. --model_name mixtral-8x7b-instruct --proxy stream --log_path data/local_demo.log # local demo
# benchmark
python batch_test.py --agent remote --api_key $api_key --model_name gpt-4 --proxy AI --log_path data/remote_batch.log --results_path data/remote_results.csv # remote benchmark
python batch_test.py --agent local --model_dir .. --model_name mixtral-8x7b-instruct --proxy batch --log_path data/local_batch.log --results_path data/local_results.csv # local benchmark
