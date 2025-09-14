import os, json
import difflib
import textwrap
from collections import OrderedDict
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display


def remove_duplicates(data):
    deduplicated = OrderedDict()

    for key, value in data.items():
        # print(key)
        if isinstance(value, list):
            deduplicated[key] = process_list(value)
        elif isinstance(value, dict):
            dict_dedup = OrderedDict()
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, list):
                    dict_dedup[sub_key] = process_list(sub_value)
                else:
                    dict_dedup[sub_key] = sub_value
            deduplicated[key] = dict_dedup
        else:
            deduplicated[key] = value
    return deduplicated


def process_list(value):
    seen = set()
    unique_list = []
    for item in value:
        if isinstance(item, (dict, list)):
            hashable_item = json.dumps(item, sort_keys=True)
        else:
            hashable_item = item

        if hashable_item not in seen:
            seen.add(hashable_item)
            unique_list.append(item)
            # print(item)
    return unique_list


def count_items(data):
    counts = {}
    for key, value in data.items():
        if isinstance(value, (list, dict)):
            if isinstance(value, list):
                counts[key] = len(value)
            else:
                counts[key] = {k: len(v) if isinstance(v, list) else 1 for k, v in value.items()}
        else:
            counts[key] = 1
    return counts


def compare_count(original, processed):
    rows = []
    print("属性条目数对比：")
    print("{:<15} {:<10} {:<10} {:<10}".format("属性", "去重前", "去重后", "变化"))
    print("-" * 45)
    for key in original:
        if isinstance(original[key], dict):
            orig = 0
            proc = 0
            for sub_key in original[key]:
                full_key = f'{key}.{sub_key}'
                orig += original[key][sub_key]
                proc += processed.get(key, {}).get(sub_key, 0)
            change = '无变化' if orig == proc else f'减少 {orig - proc}({(orig - proc) / orig})'
            rows.append({
                '属性': key,
                '去重前': orig,
                '去重后': proc,
                '变化量': orig - proc
            })
            print("{:<15} {:<10} {:<10} {:<10}".format(key, orig, proc, change))
        else:
            orig = original[key]
            proc = processed.get(key, 0)
            change = '无变化' if orig == proc else f'减少 {orig - proc}({(orig - proc) / orig})'
            rows.append({
                '属性': key,
                '去重前': orig,
                '去重后': proc,
                '变化量': orig - proc
            })
            print("{:<15} {:<10} {:<10} {:<10}".format(key, orig, proc, change))
    # print("\n示例验证：")
    # print("dataFlow 去重前:", original["dataFlow"])
    # print("dataFlow 去重后:", processed["dataFlow"])
    df = pd.DataFrame(rows)
    df["变化率(%)"] = (df["变化量"] / df["去重前"] * 100).round(2)
    return df


def highlight_changes(row):
    color = 'red' if row['变化量'] > 0 else 'green'
    return ['color: {}'.format(color) if i == 4 else '' for i in range(len(row))]


def get_compared_df(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        data = json_data['generalStats']['PATH_FLOW']
        original_counts = count_items(data)
        # print(data)
        res = remove_duplicates(data)
        deduplicated_counts = count_items(res)

        tmp_file_path = f'{file_path}_onlyPathFlow_deduplicated'
        with open(tmp_file_path, 'w') as f:
            f.write(json.dumps(res, indent=2, ensure_ascii=False))

        df = compare_count(original_counts, deduplicated_counts)
        return df
    except Exception as e:
        print(f'处理文件：{file_path}出错：{str(e)}')
    # styled_df = df.style.apply(highlight_changes, axis=1) \
    #     .format({"变化率(%)": "{:.2f}%"}) \
    #     .set_caption("JSON属性去重前后对比") \
    #     .background_gradient(subset=["变化量"], cmap="RdYlGn")
    # # 显示结果
    # print("=== 原始数据统计 ===")
    # print(pd.DataFrame.from_dict(original_counts, orient='index').rename(columns={0: '计数'}))

    # print("\n=== 去重对比DataFrame ===")
    # print(df.to_markdown())

    # # 可视化
    # ax = df.plot.bar(x='属性', y=['去重前', '去重后'],
    #                 figsize=(12, 6),
    #                 title="JSON属性条目数去重前后对比")
    # ax.set_ylabel("条目数")
    # for p in ax.patches:
    #     ax.annotate(str(p.get_height()),
    #                (p.get_x() + p.get_width() / 2., p.get_height()),
    #                ha='center', va='center',
    #                xytext=(0, 5),
    #                textcoords='offset points')
    # plt.xticks(rotation=45, ha='right')
    # plt.tight_layout()
    # plt.show()


def process_projs(root_dir):
    results = []
    subdirs = [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]
    total_count = len(subdirs)
    stat_count = 0
    for subdir in subdirs:
        proj_id = subdir.split('_')
        assert len(proj_id) == 2
        file_path = os.path.join(root_dir, subdir, 'stats')
        if os.path.exists(file_path):
            stat_count += 1
            df = get_compared_df(file_path)
            if df is not None:
                proj = proj_id[0]
                id = proj_id[1]
                res = {
                    '项目名': proj,
                    '编号': id,
                    'pathConditions去重后': df.loc[df['属性'] == 'pathConditions', '去重后'].iloc[0],
                    'dataFlow去重后': df.loc[df['属性'] == 'dataFlow', '去重后'].iloc[0]
                }
                results.append(res)
    return pd.DataFrame(results) if results else pd.DataFrame(), stat_count, total_count


def generate_boxplots(combined_df):
    if combined_df.empty:
        return
    numeric_cols = [col for col in combined_df.select_dtypes(include='number').columns
                    if col not in ['id']]
    if not numeric_cols:
        return
    projs = combined_df.groupby('项目名')[numeric_cols].sum().reset_index()

    plt.figure(figsize=(12,6))
    plt.suptitle(f'按项目分布的箱型图', y=1.02)

    for i, col in enumerate(numeric_cols, 1):
        plt.subplot(1, len(numeric_cols), i)
        plt.boxplot(projs[col])
        plt.title(col)
        plt.ylabel('总和')
    plt.tight_layout()
    plt.show()


def process_fix_to_pat(root_dir, facts=None):
    if facts is None:
        facts = {}
        buggy_function_file = 'D:\\Projects\\ThinkRepair-main\\Datasets\\RWB\\RWB-V2.0.json'
        with open(buggy_function_file, 'r', encoding='utf-8') as f:
            buggy_json = json.loads(f.read())
        for key, value in buggy_json.items():
            if key not in facts.keys():
                facts[key] = {}
            facts[key]['Buggy Function'] = buggy_json[key]['buggy']
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('java'):
                bug_name = str(file).removesuffix('.java')
                if bug_name not in facts.keys():
                    continue
                if 'User Patches' not in facts[bug_name].keys():
                    facts[bug_name]['User Patches'] = {}
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as patch_file:
                    content = patch_file.read()
                    buggy_dedent = textwrap.dedent(facts[bug_name]['Buggy Function'])
                    pat_dedent = textwrap.dedent(content)
                    diff = difflib.unified_diff(buggy_dedent.split('\n'),
                                                pat_dedent.split('\n'), fromfile="buggy", tofile="patch")
                    diff_pat = "\n".join(diff)
                with open(os.path.join(root, f'{bug_name}.patch'), 'w', encoding='utf-8') as patch_file:
                    patch_file.writelines(diff_pat)
                facts[bug_name]['User Patches'][f'RWB2-{bug_name}-1.patch'] = diff_pat
    return facts



if __name__ == '__main__':
    # root_dir = 'D:\\Projects\\python\\LLM\\res_in_turn'
    # target_column = '去重后'
    # combined_df, stat_count, total_count = process_projs(root_dir)
    # if not combined_df.empty:
    #     print("\n处理结果摘要:")
    #     print(f"总数据量: {total_count}")
    #     print(f"有效量: {stat_count}")
    #
    #     # 生成箱型图
    #     generate_boxplots(combined_df)
    #
    #     # 保存结果（可选）
    #     combined_df.to_csv(f'{root_dir}\\combined_results.csv', index=False)
    #     print("结果已保存到 combined_results.csv")
    # else:
    #     print("未找到有效数据文件")
    root_dir = 'D:\\Projects\\ThinkRepair-main\\Results\\correct_patches\\RWB'
    new_pats = process_fix_to_pat(f'{root_dir}')
    with open('RWB2_with_facts.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(new_pats, indent=4))