import pandas as pd
import re

"""
Current prompt includes one function, one comment from each ID with all relative tests and exceptions.
TODO:
1. Few-shot prompting
2. Majority voting
3. Patch extraction

Some bugs are not caused by "wrong" statements in the code, but by missing statements.
These cases must be considered in the prompt.
"""

class PromptFormatter:
    def __init__(self, func_path, msg_path):
        self.func_path = func_path
        self.msg_path = msg_path
        self.func, self.msg = self.init_data()

    def init_data(self):
        func_df = pd.read_csv(self.func_path, sep='¥', engine='python')
        msg_df = pd.read_csv(self.msg_path, sep='¥', engine='python')
        return func_df, msg_df
    
    def extract_lined_context(self, str):
        lines = re.findall(r'<line.*?>.*?(?=\n|$)', str, re.DOTALL)
        lines = [re.sub(r'(<line.*?>) \+', r'\1', line) for line in lines]
        return '\n'.join(lines)
    
    def get_one_data(self, idx):
        if isinstance(idx, int):
            func_row = self.func.iloc[idx]
            ID = func_row['ID']
            msg_rows = self.msg[self.msg['ID'] == ID]
        elif isinstance(idx, str):
            ID = idx
            func_row = self.func[self.func['ID'] == ID].iloc[0]
            msg_rows = self.msg[self.msg['ID'] == ID]
        else:
            raise ValueError("idx must be 'int' (ITER) or 'str' (ID))")

        function = func_row['replaced_method']
        comment = func_row['comment']
        exceptions = ('\n').join(msg_rows['exception_info'].to_list())
        tests = ('\n').join(msg_rows['test_method'].to_list())
        function = self.extract_lined_context(function)

        return ID, {"function": function, "comment": comment, "exceptions": exceptions, "tests": tests}
        
    def format_prompt(self, function, comment, exceptions, tests):
        prompt = f"""```markdown
[Bug Report Start]

**Function Comment of Buggy Method:**
{comment}

**Buggy Method Context:**
{function}

**Error Messages from JUnit Tests:**
{exceptions}

**Failed JUnit Tests:**
{tests}

[Bug Report End]
```"""
        return prompt.strip()
    
