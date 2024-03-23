import re
import json
import difflib
import pandas as pd

def remove_comments(code_str, lang):
    code_lines = code_str.split('\n')
    new_lines = []
    
    for line in code_lines:
        if '#' in line and '\#' not in line and 'python' in lang:
            new_line = line[:line.index('#')].rstrip()
            if new_line != '':
                new_lines.append(new_line)

        elif '//' in line and '\//' not in line and ('cpp' in lang or 'java' in lang):
            new_line = line[:line.index('//')].rstrip()
            if new_line != '':
                new_lines.append(new_line)
                
        else:
            new_lines.append(line)

    new_code_str = '\n'.join(new_lines)
    return new_code_str


def replace_diff(original, modified, pure):
    original_lines = original.split('\n')
    modified_lines = modified.split('\n')

    diff = difflib.ndiff(original_lines, modified_lines)
    output_lines = []
    in_chunk = False

    # 遍历diff
    for line in diff:
        if pure:
            ### ignore empty lines
            if line.strip() in {'+', '-'} or line.strip().startswith(('//', '/*', '*', '*/', '#', '"""', "'''")):
                continue
            # ### ignore comments in cpp or java
            # if diff.strip().startswith('//') or diff.strip().startswith('/*') or diff.strip().startswith('*') or diff.strip().startswith('*/'):
            #     continue
            # ### ignore comments in python
            # if diff.strip().startswith('#') or diff.strip().startswith('"""') or diff.strip().startswith("'''"):
            #     continue 
        if line.startswith(' '):
            if in_chunk:
                output_lines.append('<Chunk_For_Modification>')
                in_chunk = False
            output_lines.append(line[2:])
        elif line.startswith('-') or line.startswith('+'):
            if not in_chunk:
                output_lines.append('<Chunk_For_Modification>')
                in_chunk = True

    if in_chunk:
        output_lines.append('<Chunk_For_Modification>')

    output = '\n'.join(output_lines) + '\n'
    output = re.sub(r'(<Chunk_For_Modification>\n){2,}', '<Chunk_For_Modification>\n', output)

    return output.strip()

def clean_debugbench(pure=False): # pure = True # if clean all the comments

    data = json.load(open('eval.json'))

    # print(data[76]['diff'])
    # print(data[76]['located_code'])
    print(data[76]['buggy_code'])
    print(data[76]['solution'])

    """replace diff"""
    for i in range(len(data)):
        buggy_code = data[i]['buggy_code'].strip()
        fixed_code = data[i]['solution'].strip()
        lang = data[i]['language']

        if pure:
            buggy_code = remove_comments(buggy_code, lang)
            fixed_code = remove_comments(fixed_code, lang)

        bug_lines = buggy_code.split('\n')
        fix_lines = fixed_code.split('\n')
        diff = difflib.unified_diff(bug_lines, fix_lines)
        diff_str = '\n'.join(list(diff))

        located_code = replace_diff(buggy_code, fixed_code, pure)

        data[i]['diff'] = diff_str
        data[i]['located_code'] = located_code
        data[i]['buggy_code'] = buggy_code
        data[i]['solution'] = fixed_code
    if pure:
        json.dump(data, open('eval_pure.json', 'w'), indent=2)
    else:
        json.dump(data, open('eval_base.json', 'w'), indent=2)
        
    print('-'*80)
    print(data[76]['diff'])
    print(data[76]['located_code'])
    print(data[76]['buggy_code'])
    print(data[76]['solution'])

def clean_defects4j(pure=False): # pure = True # if clean all the comments

    data = pd.read_csv('lined_data2.csv', sep=',', encoding='utf-8', engine='python')
    data = data.assign(diff='', located_code='')

    """replace diff"""
    for i in range(len(data)):
        buggy_code = data['buggy_code'][i].strip()
        fixed_code = data['solution'][i].strip()
        lang = 'java'

        if pure:
            buggy_code = remove_comments(buggy_code, lang)
            fixed_code = remove_comments(fixed_code, lang)

        bug_lines = buggy_code.split('\n')
        fix_lines = fixed_code.split('\n')
        diff = difflib.unified_diff(bug_lines, fix_lines)
        diff_str = '\n'.join(list(diff))

        located_code = replace_diff(buggy_code, fixed_code, pure)

        data['diff'][i] = diff_str
        data['located_code'][i] = located_code
        data['buggy_code'][i] = buggy_code
        data['solution'][i] = fixed_code
    

    data.to_csv('lined_data2.csv', sep=',', encoding='utf-8', index=False)


if __name__ == '__main__':
    # clean_debugbench(False)
    clean_defects4j(False)

#     a = """1
# 2
# 3
# // comment
# 5
# 4
# 6
# 7"""

#     b = """1
# 2
# 3
# 4
# 4
# //comment
# 5
# 8"""
#     print('\n'.join(difflib.unified_diff(a.split('\n'), b.split('\n'))))

#     print(replace_diff(a, b, True))