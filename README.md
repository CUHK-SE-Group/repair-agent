# README

## Datasets
- Defects4J: https://github.com/rjust/defects4j
- DebugBench: https://github.com/thunlp/DebugBench

The first linked dataset is Defects4J, which contains a total of 837 bugs from the GitHub repositories. We use `utils.py` to check out and extract all the single-function data to `data/eval.csv`. We further use `data/cleaner.py` to add the reformated masked buggy program in `data/eval.csv`. The masked programs is for the experiments in RQ2.

The second linked dataset is DebugBench, which contains a total of 4,296 bugs (C++/Python/Java) from LeetCode. We also use `data/cleaner.py` to add the masked verison of the buggy programs for RQ2.

## Models
- GPT-4: https://platform.openai.com/docs/api-reference/chat
- Mixtral-8x7b-MoE: https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1

The first link is the document of OpenAI APIs, and the second link is the download page of Mixtral model.

## How to run

### Patch Generation

- Modify the first line of `batch.sh` to use your own API key: `api_key='sk-xxx'`
- run `batch.sh`

### Patch Validation

- For Defects4J:
    - Run `utils.py` to checkout the repositories in your local environment. 
    - Modify the last line of `defects4j_test_G&V.py` to enable the `verify()` method.
    - Run `defects4j_test_G&V.py`

- For DebugBench:
    - Modify the `COOKIE_LIST` of the `LeetcodeVerifier.py` to use your own LeetCode cookie.
    - Modify the last line of `debugbench_test_G&V.py` to enable the `verify()` method.
    - Run `debugbench_test_G&V.py`

## Price Calculation

Run `price.py` to gain the average price of fixing each bug (with 10 re-sampling time) on Defects4J.