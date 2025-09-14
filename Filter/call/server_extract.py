import os, re
import pandas as pd
import json


def get_srcTest():
    with open('/mnt/Benchmark_py/bugs_inputs.csv', 'r', encoding='utf-8') as f:
        df = pd.read_csv(f)
    dict_result = {row['bug_name'].lower(): row['srcTestDir'] for index, row in
                   df[['bug_name', 'srcTestDir']].iterrows()}
    return dict_result


def get_method(failing_test_line):
    pattern = r'^---\s*(?P<package_path>[^:]+)::(?P<method_name>.+)$'
    match = re.match(pattern, failing_test_line)
    if match:
        package_path = match.group('package_path')
        method_name = match.group('method_name')
        return package_path.replace('.', '/'), method_name
    else:
        print(f'字符串解析不正确：{failing_test_line}')
        return '', ''


def extract_test_from_java(cls_path, mth):
    function_content = ""
    function_pattern = re.compile(rf'public\s+void\s+{mth}\s*\([^)]*\)\s*(throws\s+[\w\s,]+)?\s*\{{(.*?)}}', re.DOTALL)
    try:
        with open(cls_path, 'r', encoding='utf-8') as file:
            content = file.read()
            match = function_pattern.search(content)
            if match:
                function_content = match.group(0)
            else:
                print(f"未找到函数: {mth}")
    except FileNotFoundError:
        print(f"文件未找到: {cls_path}")
    except Exception as e:
        print(f"发生错误: {e}")
    return function_content


facts_json = {}
data = get_srcTest()
for root, dirs, files in os.walk('/mnt/PDA_trace/bugs'):
    for dir_name in dirs:
        dir_path = os.path.join(root, dir_name)
        if not dir_path.endswith('_buggy'):
            continue
        bug_name = dir_name.removesuffix('_buggy')
        print('proceeding for bug ' + bug_name)
        failing_test_file = os.path.join(dir_path, 'failing_tests')
        with open(failing_test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        tests = {'Trigger tests': []}
        for index, line in enumerate(lines):
            if line.startswith('---'):
                cls, mth = get_method(line)
                cls_path = os.path.join(dir_path, data[bug_name] + "_purify", cls) + ".java"
                test_function = extract_test_from_java(cls_path, mth)
                tests['Trigger tests'].append({
                    'exception_info': '\n'.join(lines[index:index + 10]),
                    'test_function': test_function
                })
        facts_json[bug_name] = tests
output = '/mnt/PDA_trace/bugs/trigger_tests_facts.json'
with open(output, 'w') as f:
    f.write(json.dumps(facts_json, indent=4))
