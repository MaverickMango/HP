import os, sys
import json

import pandas as pd

mapping = {
    'cli': 'Cli',
    'closure': 'Closure',
    'codec': 'Codec',
    'compress': 'Compress',
    'gson': 'Gson',
    'jacksoncore': 'JacksonCore',
    'jsoup': 'Jsoup',
    'lang': 'Lang',
    'math': 'Math',
    'mockito': 'Mockito',
    'time': 'Time'
}


def get_tests(tests_file):
    tests = {}
    with open(tests_file, 'r', encoding='utf-8') as f:
        json_data = json.loads(f.read())
    for key, value in json_data.items():
        splits = key.split('_')
        assert len(splits) == 2
        if splits[0] in mapping.keys():
            new_key = '-'.join([mapping[splits[0]], splits[1]])
            tests[new_key] = value
        else:
            print(f'没考虑到的项目名：{splits[0]}')
    return tests


def get_patches(root_directory, postfix, contains=True):
    patches = {}
    for root, _, files in os.walk(root_directory):
        for file in files:
            flag = file.endswith(postfix) if contains else postfix not in file
            if flag:
                splits = file.split('-')
                if len(splits) < 3:
                    bug_name = str(file).removesuffix('.patch').replace('_', '-')
                else:
                    bug_name = '-'.join([splits[1], splits[2]])
                if bug_name not in patches.keys():
                    patches[bug_name] = {}
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as patch_file:
                    content = patch_file.read()
                    patches[bug_name][file] = content
    return patches


def get_prompt(bug_names):
    prompts = dict()
    try:
        for bug_name in bug_names:
            prompts[bug_name] = {
                'Buggy Function': '',
                'Inducing Changes': '',
            }
            info_file = bug_name.replace('-', '_')
            with open(f'data/changesInfo/{info_file}/origianl_fixing_info.json', 'r', encoding='utf-8') as f:
                json_data = json.loads(f.read())
                bics = json_data['inducing_changes']
                fcs = json_data['fixing_changes']
                for fc in fcs:
                    changed_cls = fc['changed_class'][0]
                    matching_objects = [bic for bic in bics if bic['changed_class'][0] == changed_cls]
                    for obj in matching_objects:
                        prompts[bug_name]['Inducing Changes'] = obj['diff'] + '\n'
            # prompts[bug_name] = {
            #     'Variables': '',
            #     'Declarators': '',
            #     'DataFlows': '',
            #     'Constraints': '',
            #     'Buggy Function': ''
            # }
            # stat_name = bug_name.replace('-', '_')
            # curr_file = [s for s in stats if stat_name in s][0]
            # with open(curr_file, 'r', encoding='utf-8') as f:
            #     json_data = json.loads(f.read())
            #     prompts[bug_name]['Constraints'] = json_data['pathConditions']
            #     prompts[bug_name]['DataFlows'] = json_data['dataFlow']
            #     prompts[bug_name]['Declarators'] = json_data['declarators']
            #     prompts[bug_name]['Variables'] = json_data['variables']
        with open('single_function_repair.json', 'r', encoding='utf-8') as f:
            json_data = json.loads(f.read())
        for key, value in json_data.items():
            if key not in bug_names:
                continue
            prompts[key]['Buggy Function'] = value['buggy']
    except Exception as e:
        print(f'处理json文件出错：{str(e)}')
    return prompts


def process_projs(root_dir, patches):
    results = []
    subdirs = [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]
    total_count = len(subdirs)
    stat_count = 0
    bug_names = []
    stats = []
    for subdir in subdirs:
        proj_id = subdir.replace('_', '-')
        file_path = os.path.join(root_dir, subdir, 'stats_onlyPathFlow_deduplicated')
        if not os.path.exists(file_path):
            continue
        bug_names.append(proj_id)
        stats.append(file_path)
    prompts = get_prompt(bug_names)
    for key, value in prompts.items():
        if key in patches.keys():
            prompts[key]['User Patches'] = patches.get(key)
    return prompts


def get_prompts_for_all_bugs(patches):
    with open('D:\\Projects\\python\\LLM\\bugs_inputs.csv', 'r', encoding='utf-8') as f:
        bugs_df = pd.read_csv(f)
    bug_names = bugs_df['bug_name'].tolist()
    bug_names = [n.replace('_', '-') for n in bug_names]
    prompts = get_prompt(bug_names)
    return prompts


def add_patches_to_facts(facts_file, patches, facts_json=None):
    if facts_json is None:
        with open(facts_file, 'r', encoding='utf-8') as f:
            facts_json = json.loads(f.read())
    for key, value in facts_json.items():
        proj_id = key
        if 'User Patches' not in value.keys():
            value['User Patches'] = {}
        if proj_id in patches.keys():
            value['User Patches'].update(patches[key])
    prompt = facts_json
    return prompt


def add_trigger_tests_to_prompts(facts_file, trigger_tests, facts_json=None):
    if facts_json is None:
        with open(facts_file, 'r', encoding='utf-8') as f:
            facts_json = json.loads(f.read())
    for key, value in facts_json.items():
        proj_id = key
        if proj_id in trigger_tests.keys():
            value.update(trigger_tests[key])
    prompt = facts_json
    return prompt


def add_bic_to_prompt(facts_file, bic_file):
    with open(facts_file, 'r', encoding='utf-8') as f:
        facts_json = json.loads(f.read())
    with open(bic_file, 'r', encoding='utf-8') as f:
        bic_json = json.loads(f.read())
    count = 0
    for key, value in facts_json.items():
        pro_id = key
        if pro_id in bic_json.keys():
            value['Inducing Changes'] = bic_json[pro_id]['Inducing Changes']
            value['Trigger tests'] = bic_json[pro_id]['Trigger tests']
            count += 1
        else:
            value['Inducing Changes'] = ""
    prompt = facts_json
    return prompt



if __name__ == '__main__':
    # root_dir = 'D:\\Projects\\python\\LLM\\res_in_turn'
    # icse_patches = get_patches('D:\\Projects\\Patches\\Patches_ICSE\\Doverfitting', '.patch')
    # # # icse_same_patches = get_patches('D:\\Projects\\Patches\\Patches_ICSE\\Dsame', '.patch')
    # llm_patches = get_patches('D:\\Projects\\Filtered_D4JPatches-main\\plausible patches\\pass_all_test\\all\\patch', '.', False)
    # # correct_patches = get_patches('D:\\Projects\\Filtered_D4JPatches-main\\correct', '.patch')
    # # patches = icse_patches#llm_patches
    # # prompts = process_projs(root_dir, patches)
    # facts_file = 'D:\\Projects\\python\\LLM\\facts.json'
    # tests = get_tests('D:\\Projects\\python\\LLM\\trigger_tests_facts.json')
    # prompt = add_trigger_tests_to_prompts(facts_file, tests)
    # prompt = add_patches_to_facts(facts_file, icse_patches, prompt)
    # prompt = add_patches_to_facts(facts_file, llm_patches, prompt)
    # # prompt = add_patches_to_facts(facts_file, correct_patches, prompt)
    # with open('icse&llm_plausible_with_tests.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(prompt, indent=4))

    facts_file = 'D:\\Projects\\python\\LLM\\new_with_facts.json'
    bic_file = 'D:\\Projects\\python\\LLM\\correct_with_tests.json'
    prompt = add_bic_to_prompt(facts_file, bic_file)
    with open('new_with_tests.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(prompt, indent=4))