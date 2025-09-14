import json
import os, re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import matplotlib
import plotly
from tabulate import tabulate
# 设置全局字体为支持中文的字体
matplotlib.rcParams['font.family'] = 'Microsoft YaHei'  # 或者 'Microsoft YaHei'
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

pattern_only_pat = r'''
\{
    \s*"verdict":\s*(")?(correct|incorrect)(")?
    \s*,\s*  # 逗号分隔符
    "explanation":\s*"
        (?:  # 字符串内容（非捕获组）
            [^"\\]  # 非引号/反斜杠字符
            |  # 或
            \\.  # 转义序列如 \" 或 \\
        )*  # 重复任意次
    "\s*
\}
'''
pattern = r'''
\{
    \s*"verdict":\s*(")?(correct|incorrect)(")?
    (?:\s*,\s*"confidence":\s*-?\d+\.\d+)?  # 浮点数（可选负号、整数+小数部分）
    (?:\s*,\s*"inverse":\s*\b(true|false)\b)?
    \s*,\s*"behavioral_coverage":\s* 
    \{  
        (?:\s*"core":\s*-?\d+(\.\d+)?)?  # 浮点数
        (?:\s*,\s*"edge_cases":\s*-?\d+(\.\d+)?)?  # 浮点数
        (?:\s*,\s*"error_behavior":\s*-?\d+(\.\d+)?)?
        (?:\s*,\s*"defensive_bonus":\s*-?\d+(\.\d+)?)?
        (?:\s*,\s*"unknown_impact_penalty":\s*-?\d+(\.\d+)?)?  #浮点数
    \s*\}  # 嵌套对象结束
    \s*(?:,\s*  # 逗号分隔符
    "explanation":\s*"
        (?:  # 字符串内容（非捕获组）
            [^"\\]  # 非引号/反斜杠字符
            |  # 或
            \\.  # 转义序列如 \" 或 \\
        )*  # 重复任意次
    "\s*)?
\}
'''


def read_file_in_chunks(file_path, chunk_size=9):
    with open(file_path, 'r', encoding='utf-8') as file:
        chunk = []
        for line in file:
            chunk.append(line.strip())  # 去掉每行的首尾空白字符
            if len(chunk) == chunk_size:
                yield chunk
                chunk = []  # 重置块
        if chunk:  # 如果文件最后一块不足 chunk_size 行，也返回
            yield chunk


def pure_json_res_for_each_patch(res_root, pattern):
    for root, _, files in os.walk(res_root):
        for file in files:
            has_already_split = any(f.endswith('.patch') for f in files)
            # if has_already_split:
            #     continue
            file_path = os.path.join(root, file)
            print(file_path)
            # if file.endswith('.txt'):
            #     content = {}
            #     assert file == 'plausible_deepseek-r1.txt'
            #     for chunk in read_file_in_chunks(file_path, chunk_size=9):
            #         json_str = '{' + ''.join(chunk) + '}'
            #         try:
            #             patch = json.loads(json_str)
            #             for key, value in patch.items():
            #                 content[key] = json.dumps(value)
            #         except json.JSONDecodeError as e:
            #             print("JSON 解析失败：", e)
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as res_file:
                    content = json.loads(res_file.read())
            else:
                continue
            for key, value in content.items():
                if not key.endswith('.patch'):
                    key += '.patch'
                # print(value)
                if value == 'null':
                    print("没有输出：" + key)
                    continue
                # if '###' in str(value) or "```json" in str(value):
                # extract json object
                regex = re.compile(pattern, re.VERBOSE)
                match = regex.search(value)
                if not match:
                    print("匹配失败：" + value)
                    continue
                else:
                    value = match.group()
                if '"correct"' in value or '"incorrect"' in value:
                    pass
                elif '"verdict": correct' in value:
                    value = value.replace('"verdict": correct', '"verdict": "correct"')
                elif '"verdict": incorrect' in value:
                    value = value.replace('"verdict": incorrect', '"verdict": "incorrect"')
                value = value.replace('\n', '')
                json_value = json.loads(str(value))
                if 'inverse' not in json_value.keys():
                    json_value['inverse'] = False
                if 'confidence' not in json_value.keys():
                    json_value['confidence'] = 0.0
                if 'core' not in json_value.keys():
                    json_value['core'] = 0.0
                if 'edge_cases' not in json_value.keys():
                    json_value['edge_cases'] = 0.0
                if 'error_behavior' not in json_value.keys():
                    json_value['error_behavior'] = 0.0
                if 'unknown_impact_penalty' not in json_value.keys():
                    json_value['unknown_impact_penalty'] = 0.0
                if 'defensive_bonus' not in json_value.keys():
                    json_value['defensive_bonus'] = 0.0
                if 'explanation' not in json_value.keys():
                    json_value['explanation'] = ""
                with open(f'{root}/{key}', 'w', encoding='utf-8') as res_file:
                    res_file.write(json.dumps(json_value, indent=4))


def data_process(data, output_file, dpattern):
    # 压表
    df = pd.DataFrame(data).T.reset_index()
    # print(df['behavioral_coverage'].iloc[0])
    if 'behavioral_coverage' in df.columns:
        behavior_expanded = pd.json_normalize(df['behavioral_coverage'])
        df = df.drop('behavioral_coverage', axis=1)
        df = pd.concat([df, behavior_expanded], axis=1)
    df = df.rename(columns={'level_0': 'proj', 'level_1': 'bid', 'level_2': 'tool', 'level_3': 'genuine'})
    print(df.columns)
    df.to_csv(output_file, index=False, encoding='utf-8')

    if dpattern == pattern:
        metrics = ['confidence', 'inverse', 'core', 'edge_cases',
               'error_behavior', 'defensive_bonus', 'unknown_impact_penalty']
        df_metrics = df[metrics].astype(float)
    else:
        df_metrics = None
    print(f'总计数据数：{len(df)}')
    return df, df_metrics


def numeric_analysis(df_metrics):
    if df_metrics is None:
        return
    # 数值部分分析
    analysis_table = df_metrics.describe(percentiles=[.25, .5, .75]).loc[['min', 'max', 'mean', '50%', 'std']]
    analysis_table.index = ['MIN', 'MAX', 'MEAN', 'MEDIAN', 'STD DEV']
    print(tabulate(
        analysis_table.reset_index(),
        headers=['Metric'] + analysis_table.columns.tolist(),
        tablefmt='pipe',
        floatfmt='.2f',
        stralign='center'
    ))
    return analysis_table


def numeric_plot(df_metrics):
    if df_metrics is None:
        return
    fig, axs = plt.subplots(1, len(df_metrics.columns), figsize=(16, 6), sharey=True)
    fig.suptitle('指标分布统计', fontsize=16, fontweight='bold')
    # 为每个指标创建箱线图
    for i, col in enumerate(df_metrics.columns):
        # 箱线图
        bp = axs[i].boxplot(
            df_metrics[col],
            vert=True,
            patch_artist=True,
            widths=0.6,
            boxprops=dict(facecolor='lightblue', linewidth=2),
            medianprops=dict(color='red', linewidth=2),
            flierprops=dict(marker='o', markersize=5, markerfacecolor='grey'),
            whiskerprops=dict(linewidth=1.5),
            capprops=dict(linewidth=1.5)
        )
        # 计算统计值
        min_val = df_metrics[col].min()
        max_val = df_metrics[col].max()
        mean_val = df_metrics[col].mean()
        median_val = df_metrics[col].median()
        std_val = df_metrics[col].std()

        # 添加统计值标记 - 使用文本标签而非位置标记
        stats_text = (
            f"最小值: {min_val}\n" # :.2f
            f"最大值: {max_val}\n" # :.2f
            f"平均值: {mean_val}\n" # :.2f
            f"中位数: {median_val}\n" # :.2f
            f"标准差: {std_val}" # :.2f
        )
        anchored_text= AnchoredText(
            stats_text,
            loc='lower right',
            frameon=True,
            bbox_to_anchor=(1, 0),
            bbox_transform=axs[i].transAxes,
            borderpad=0.6,
            prop=dict(size=10)
        )
        anchored_text.patch.set(
            boxstyle='round,pad=0.2',
            facecolor='#fff8dc',
            alpha=0.9,
            edgecolor='#daa520'
        )
        axs[i].add_artist(anchored_text)

        # # 将统计文本放在图表右侧
        # axs[i].text(
        #     1.02, 0.95, stats_text,
        #     transform=axs[i].transAxes,
        #     fontsize=10,
        #     verticalalignment='top',
        #     horizontalalignment='left',
        #     bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        # )

        # 设置图表标题和标签
        axs[i].set_title(col, fontsize=12)
        axs[i].set_xticks([1])
        axs[i].set_xticklabels([col.split('.')[-1]])
        axs[i].grid(True, linestyle='--', alpha=0.3)

        # 保证箱型图居中
        axs[i].set_xlim(0.5, 1.5)

        # 设置Y轴范围（0-1）
        axs[i].set_ylim(-0.05, 1.05)
        axs[i].set_yticks(np.arange(0, 1.1, 0.2))
    fig.text(0.04, 0.5, 'Metrics', va='center', rotation='vertical', fontsize=12)
    plt.tight_layout(rect=[0.04, 0, 1, 0.95])
    plt.subplots_adjust(wspace=0.1)
    plt.show()


def head_map(metrics, df_metrics):
    # 按指标画图
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    for i, col in enumerate(metrics):
        ax = axes[i//2, i%2]
        df_metrics[col].hist(ax=ax, bins=15, alpha=0.7)
        ax.set_title(f'Distribution of {col.split('.')[-1]}')
    plt.tight_layout()
    plt.show()


def get_result_csv(res_root, gpattern):
    pure_json_res_for_each_patch(res_root, gpattern)
    data = {}
    for root, _, files in os.walk(res_root):
        for file in files:
            if file.endswith('.patch'):
                file = file.removesuffix('.patch')
                splits = file.split('-')
                if len(splits) < 4:
                    proj_id = str(file)
                    proj = proj_id.split('_')[0]
                    bid = proj_id.split('_')[1]
                    tool = 'developer'
                    genuine = 'correct'
                elif file.startswith('patch'):
                    proj = splits[1]
                    bid = splits[2]
                    tool = splits[3]
                    genuine = splits[4] if len(splits) > 4 else 'plausible'
                else:
                    proj = splits[1]
                    bid = splits[2]
                    tool = splits[0] + '-' + splits[3]
                    genuine = 'plausible'
                with open(os.path.join(root, f'{file}.patch'), 'r', encoding='utf-8') as f:
                    result = json.loads(f.read())
                data[(proj, bid, tool, genuine)] = result
    df, df_metrics = data_process(data, output_file=f'{res_root}/result_data.csv', dpattern=gpattern)
    # numeric_analysis(df_metrics)
    numeric_plot(df_metrics)


if __name__ == '__main__':
    res_root = 'claude-3-5-haiku-20241022\\icse&llm_plausible_classify_res'
    get_result_csv(res_root, gpattern=pattern)