import json
import sys, os
import chatbot as cb
import system_prompt
import logging


def call_with_facts(prompts_file, model_name, stream=False):
    with open(prompts_file, 'r', encoding='utf-8') as f:
        json_data = json.loads(f.read())
    # do for each bug
    for key, value in json_data.items():
        bug_name = key
        # if 'JacksonCore' in bug_name:
        #     continue
        # if bug_name == 'JacksonCore-5':
        #     continue
        if value['Buggy Function'] == '' or value['Inducing Changes'] == '':
            logging.debug(bug_name)
            continue
        if 'User Patches' not in value.keys():
            continue
        splits = prompts_file.split('_')
        prefix = '_'.join(splits[:2])
        target_dir = f'{prefix}_classify_res/{key.split('-')[0]}/{key}'
        # if os.path.exists(target_dir):
        #     continue
        # value.pop('Inducing Changes')
        # value.pop('Trigger tests')
        patches = value.pop('User Patches')  # json object
        prompt_prefix = value  # json object

        chatbot = cb.ChatBot(prompt_prefix=prompt_prefix, model=model_name)

        json_output = {}
        for patch_name, content in patches.items():
            if os.path.exists(f'{target_dir}/{patch_name}'):
                if os.path.exists(f'{target_dir}/{patch_name}.patch'):
                    continue
            user = '\"User Patches\": '
            prompt = f'{user} \"{content}\"'
            res = chatbot.chat(prompt, False, stream=stream)
            logging.info(f'\"{patch_name}\": {res}')
            json_output[patch_name] = res

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        with open(f'{target_dir}/{prefix}_{model_name}.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(json_output, indent=4))


# def call_only_patch_with_buggy(prompts_file, model_name, stream=False):
#     with open(prompts_file, 'r', encoding='utf-8') as f:
#         json_data = json.loads(f.read())
#     # do for each bug
#     for key, value in json_data.items():
#         bug_name = key
#         if value['Buggy Function'] == '' or 'User Patches' not in value.keys():
#             continue
#         splits = prompts_file.split('_')
#         prefix = '_'.join(splits[:2])
#         target_dir = f'{prefix}_classify_res/{key.split('-')[0]}/{key}'
#         if os.path.exists(target_dir):
#             continue
#         patches = value.pop('User Patches')  # json object
#         prompt_prefix = '###Buggy Function\n'
#         prompt_prefix += value['Buggy Function']
#
#         chatbot = cb.ChatBot(system_prompt=system_prompt.patch_only,
#                              prompt_prefix=prompt_prefix,
#                              model=model_name)
#
#         json_output = {}
#         for patch_name, content in patches.items():
#             user = '\"User Patches\": '
#             prompt = f'{user} \"{content}\"'
#             res = chatbot.chat(prompt, False, stream=stream)
#             logging.info(f'\"{patch_name}\": {res}')
#             json_output[patch_name] = res
#
#         if not os.path.exists(target_dir):
#             os.makedirs(target_dir)
#         with open(f'{target_dir}/{prefix}_{model_name}.json', 'w', encoding='utf-8') as f:
#             f.write(json.dumps(json_output, indent=4))


def call_only_simple_prompt(prompts_file, model_name, stream=False):
    with open(prompts_file, 'r', encoding='utf-8') as f:
        json_data = json.loads(f.read())
    # do for each bug
    for key, value in json_data.items():
        bug_name = key
        if value['Buggy Function'] == '' or 'User Patches' not in value.keys():
            continue
        splits = prompts_file.split('_')
        prefix = '_'.join(splits[:2])
        target_dir = f'{prefix}_classify_res/{key.split('-')[0]}/{key}'
        if os.path.exists(target_dir):
            continue
        value.pop('Inducing Changes')
        patches = value.pop('User Patches')  # json object
        prompt_prefix = value  # json object

        chatbot = cb.ChatBot(system_prompt=system_prompt.patch_only,
                             prompt_prefix=prompt_prefix,
                             model=model_name)

        json_output = {}
        for patch_name, content in patches.items():
            user = '\"User Patches\": '
            prompt = f'{user} \"{content}\"'
            res = chatbot.chat(prompt, False, stream=stream)
            logging.info(f'\"{patch_name}\": {res}')
            json_output[patch_name] = res

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        with open(f'{target_dir}/{prefix}_{model_name}.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(json_output, indent=4))


def call_with_simple_facts(prompts_file, model_name, stream=False):
    with open(prompts_file, 'r', encoding='utf-8') as f:
        json_data = json.loads(f.read())
    # do for each bug
    for key, value in json_data.items():
        bug_name = key
        # if 'JacksonCore' in bug_name:
        #     continue
        # if bug_name == 'JacksonCore-5':
        #     continue
        if value['Buggy Function'] == '' or value['Inducing Changes'] == '':
            logging.debug(bug_name)
            continue
        if 'User Patches' not in value.keys():
            continue
        splits = prompts_file.split('_')
        prefix = '_'.join(splits[:2])
        target_dir = f'{prefix}_classify_res/{key.split('-')[0]}/{key}'
        # if os.path.exists(target_dir):
        #     continue
        patches = value.pop('User Patches')  # json object
        prompt_prefix = value  # json object

        chatbot = cb.ChatBot(system_prompt=system_prompt.patch_only,
                             prompt_prefix=prompt_prefix,
                             model=model_name)

        json_output = {}
        for patch_name, content in patches.items():
            if os.path.exists(f'{target_dir}/{patch_name}'):
                if os.path.exists(f'{target_dir}/{patch_name}.patch'):
                    continue
            user = '\"User Patches\": '
            prompt = f'{user} \"{content}\"'
            res = chatbot.chat(prompt, False, stream=stream)
            logging.info(f'\"{patch_name}\": {res}')
            json_output[patch_name] = res

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        with open(f'{target_dir}/{prefix}_{model_name}.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(json_output, indent=4))


def call_with_simple_no_original(prompts_file, model_name, stream=False):
    with open(prompts_file, 'r', encoding='utf-8') as f:
        json_data = json.loads(f.read())
    # do for each bug
    for key, value in json_data.items():
        bug_name = key
        # if 'JacksonCore' in bug_name:
        #     continue
        # if bug_name == 'JacksonCore-5':
        #     continue
        if value['Buggy Function'] == '' or value['Inducing Changes'] == '':
            logging.debug(bug_name)
            continue
        if 'User Patches' not in value.keys():
            continue
        splits = prompts_file.split('_')
        prefix = '_'.join(splits[:2])
        target_dir = f'{prefix}_classify_res/{key.split('-')[0]}/{key}'
        # if os.path.exists(target_dir):
        #     continue
        value.pop('Inducing Changes')
        patches = value.pop('User Patches')  # json object
        prompt_prefix = value  # json object

        chatbot = cb.ChatBot(system_prompt=system_prompt.apca7,
                             prompt_prefix=prompt_prefix,
                             model=model_name)

        json_output = {}
        for patch_name, content in patches.items():
            if os.path.exists(f'{target_dir}/{patch_name}'):
                if os.path.exists(f'{target_dir}/{patch_name}.patch'):
                    continue
            user = '\"User Patches\": '
            prompt = f'{user} \"{content}\"'
            res = chatbot.chat(prompt, False, stream=stream)
            logging.info(f'\"{patch_name}\": {res}')
            json_output[patch_name] = res

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        with open(f'{target_dir}/{prefix}_{model_name}.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(json_output, indent=4))


if __name__ == '__main__':

    # custom_output = CustomOutput()
    # original_stdout = sys.stdout
    # sys.stdout = custom_output

    model_name = 'gpt-4-1106-preview_new0'
    prompts_file = 'icse&llm_plausible_with_tests.json'
    logging.basicConfig(filename=f'{model_name}_{prompts_file}.log',
                        level=logging.INFO)

    # call_only_simple_prompt(prompts_file, model_name, True)
    call_with_facts(prompts_file, model_name, True)
    # prompts_file = 'new_with_tests.json'
    # call_with_facts(prompts_file, model_name)

    # sys.stdout = original_stdout