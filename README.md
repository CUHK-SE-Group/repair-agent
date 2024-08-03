# README

## Datasets
- Defects4J: https://github.com/rjust/defects4j
- DebugBench: https://github.com/thunlp/DebugBench

The first linked dataset is Defects4J, which contains a total of 837 bugs from the GitHub repositories. We use `utils.py` to check out and extract all the single-function data to `data/eval.csv`. We further use `data/cleaner.py` to add the reformated masked buggy program in `data/eval.csv`. The masked programs is for the experiments in RQ2.

The second linked dataset is DebugBench, which contains a total of 4,296 bugs (C++/Python/Java) from LeetCode. We also use `data/cleaner.py` to add the masked verison of the buggy programs for RQ2.

We have already extract these data in `data` directory.

- Defects4J: The buggy code and developer patch are in `eval.csv`. The test information and exception messages are in `exceptions.csv`.
- DebugBench: All the data is in `eval.json`.

## Models

- GPT-4: https://platform.openai.com/docs/api-reference/chat
- Mixtral-8x7b-MoE: https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1

The first link is the document of OpenAI APIs, and the second link is the download page of Mixtral model.

## Scripts

The entry of the script is `batch.sh`. The main scripts for Defects4J and DebugBench Experiments are `defects4j_test_G&V.py` and `debugbench_test_G&V.py`

## How to run

### Environment Preparation

- Install the Python library dependencies listed in `requirements.txt`.

- Modify the first line of `batch.sh` to use your own API key: `api_key='sk-xxx'`
    - To obtain an OpenAI API Key to start generation. 
    - See [OpenAI Platform](https://platform.openai.com/api-keys) to understand how to get your own API key.
- Modify the `COOKIE_LIST` of the `LeetcodeVerifier.py` to use your own `LEETCODE_SESSION` and `csrf_token` cookie.
    - To obtain the `LEETCODE_SESSION` and `csrf_token` cookie, you may first login your LeetCode account and utilize the developer view in web browser like Chrome or use browser extensions like [EditThisCookie](https://chromewebstore.google.com/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg?pli=1). 
    - The `leetcode_env` package comes from [Leetcode Hard Gym](https://github.com/GammaTauAI/leetcode-hard-gym). More implementation details are available in [DebugBench GitHub](https://github.com/thunlp/DebugBench) and [DebugBench Huggingface](https://huggingface.co/datasets/Rtian/DebugBench)
- Run `utils.py` to checkout the Defects4J repositories and corresponding test suites in your local environment. 
    - Before checkout, please ensure the `defects4j` command is valid in your environment. Use `defects4j info -p Lang` to check installation. If not installed, please install [here](https://github.com/rjust/defects4j).
    - After checkout, the code and test are in the `defects4j` directory.

### Patch Generation & Validation

- Directly run `batch.sh`.
    - The script validates the generated patches simultaneously while generating patches.
    - The relationship between the script and the RQ experiments can be found in the comments inside `batch.sh`.

- To obtain the experimental results in a non-perfect FL setting, you should first download [FLUCCS](https://bitbucket.org/teamcoinse/fluccs/src/master/), a method-level fault localization tool. Then, find the common buggy methods located by FLUCCS in Defects4J v1.2 and correctly fixed by D4C to get the results.

## Results

After running `batch.sh`, the generated patches and validation results are in the `result` directory. CSV files starting with `results` contain the patches, and those starting with `evaluation` contain the validation results. 

We provide archived results of D4C in our experiments, marked with `_archived` suffix, include Defects4J results from GPT-4 and DebugBench results from both GPT-4 and Mixtral.

Check [here](result/defects4j/evaluation_agent_1shot_gpt-4_10try_temp=1.0_archived.csv) to find the bugs that passed all JUnit tests in Defects4J

## Price Calculation

Run `price.py` to gain the average price ($0.23) of fixing each bug (with 10 re-sampling time) on Defects4J.