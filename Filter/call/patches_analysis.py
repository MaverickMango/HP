import json
import pandas as pd
import os


def extract_pats_from_files(file_paths):
    all_pats_data = []

    print("--- 开始处理JSON文件 ---")
    for file_path in file_paths:
        try:
            filename = os.path.basename(file_path)
            print(f"正在读取文件: {filename}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, dict):
                print(f"警告: 文件 {filename} 的顶层结构不是一个字典，已跳过。")
                continue

            #proj,bid,tool,genuine
            for top_key, top_level_value in data.items():
                if isinstance(top_level_value, dict) and 'User Patches' in top_level_value:
                    pats_dict = top_level_value['User Patches']
                    proj = top_key.split('-')[0]
                    bid = top_key.split('-')[1]
                    if isinstance(pats_dict, dict):
                        for pat_key in pats_dict.keys():
                            pat_key = pat_key.removesuffix(".patch")
                            splits = pat_key.split('-')
                            if len(splits) < 4:
                                pid = ''
                                tool = 'developer'
                                genuine = 'True'
                            elif pat_key.startswith('patch'):
                                pid = splits[0]
                                tool = splits[3]
                                genuine = splits[4] if len(splits) > 4 else 'plausible'
                                if 'plausible' in genuine:
                                    genuine = 'False'
                                else:
                                    genuine = 'True'
                            else:
                                tool = splits[0]
                                pid = splits[3]
                                genuine = 'False'
                            all_pats_data.append({
                                'proj': proj,
                                'bid': bid,
                                'tool': tool,
                                'pid': pid,
                                'genuine': genuine
                            })

        except FileNotFoundError:
            print(f"错误: 文件未找到 - {file_path}。请检查路径是否正确。")
        except json.JSONDecodeError:
            print(f"错误: 文件 {file_path} 不是一个有效的JSON格式文件。")
        except Exception as e:
            print(f"处理文件 {file_path} 时发生未知错误: {e}")

    if not all_pats_data:
        print("\n未能从文件中提取到任何 'patch' 数据。")
        return None

    # 将结果列表转换为Pandas DataFrame
    result_df = pd.DataFrame(all_pats_data)
    print("\n--- 数据提取完成 ---")
    return result_df


def df_analyze(df, output_csv_path):
    initial_rows = len(df)

    # bid_counts = pd.pivot_table(
    #     df,
    #     index='tool',
    #     columns='proj',
    #     values='bid',
    #     aggfunc='nunique',
    #     fill_value='0'
    # )
    # print("'按工具统计各项目的BID数量'完成。\n")

    proj_counts = pd.pivot_table(
        df,
        index='tool',
        columns='proj',
        values='pid',
        aggfunc='count',
        fill_value='0'
    )
    print("已完成按项目的补丁数量统计。")

    if df['genuine'].dtype != bool:
        df['genuine'] = df['genuine'].astype(str).str.lower().isin(['true', '1'])
    genuine_counts = pd.pivot_table(
        df,
        index='tool',
        columns='genuine',
        values='pid',
        aggfunc='count',
        fill_value=0
    )
    if True not in genuine_counts.columns:
        genuine_counts[True] = 0
    if False not in genuine_counts.columns:
        genuine_counts[False] = 0

    genuine_counts.rename(columns={
        True: 'correct_patches_count',
        False: 'incorrect_patches_count'
    }, inplace=True)
    print("已完成正确/不正确补丁的数量统计。")

    final_df = pd.concat([proj_counts, genuine_counts], axis=1)

    # 6. 将 'tool' 从索引变回普通列，并整理输出
    final_df.reset_index(inplace=True)

    # # --- 任务 1: 计算每个工具覆盖的唯一 BID 总数 ---
    # print("[1/2] 正在计算每个工具覆盖的唯一BID总数...")
    # # 按 'tool' 分组，然后对每个组内的 'bid' 列计算唯一值的数量 (nunique)
    # bid_counts = df.groupby('tool')['bid'].nunique()
    # # 将结果转换为 DataFrame 并重命名列
    # bid_counts_df = bid_counts.reset_index(name='total_bid_count')
    # print("唯一BID总数计算完成。\n")
    #
    # # --- 任务 2: 计算每个工具生成的正确/不正确补丁总数 ---
    # print("[2/2] 正在计算每个工具的正确/不正确补丁总数...")
    # # 首先，为确保每个补丁只被计算一次，根据主键进行去重
    # df_patches = df.drop_duplicates(subset=['proj', 'bid', 'tool', 'pid']).copy()
    #
    # # 统一 'genuine' 列的格式为布尔型
    # df_patches['genuine'] = df_patches['genuine'].astype(str).str.lower().isin(['true', '1'])
    #
    # # 按 'tool' 和 'genuine' 分组，计算每组的大小（即补丁数）
    # patch_counts = df_patches.groupby(['tool', 'genuine']).size()
    #
    # # 使用 unstack 将 'genuine' 索引层转换为列
    # patch_counts_pivoted = patch_counts.unstack(level='genuine', fill_value=0)
    #
    # # --- 健壮性处理：确保 True 和 False 列都存在 ---
    # if True not in patch_counts_pivoted.columns:
    #     patch_counts_pivoted[True] = 0
    # if False not in patch_counts_pivoted.columns:
    #     patch_counts_pivoted[False] = 0
    #
    # # 重命名列以获得清晰的表头
    # patch_counts_pivoted.rename(columns={
    #     True: 'correct_patches_count',
    #     False: 'incorrect_patches_count'
    # }, inplace=True)
    # print("正确/不正确补丁总数计算完成。\n")
    #
    # # --- 合并两个统计结果 ---
    # # 使用 pd.merge 将两个基于 'tool' 列的 DataFrame 合并在一起
    # # 使用 how='outer' 以确保即使某个工具只有BID信息或只有补丁信息也能被包含进来
    # final_df = pd.merge(bid_counts_df, patch_counts_pivoted, on='tool', how='outer')
    #
    # # 合并后可能会产生NaN，比如某个工具没有生成任何补丁，将其填充为0
    # final_df.fillna(0, inplace=True)
    #
    # # 将浮点数列（如果因NaN产生）转换为整数
    # int_columns = ['total_bid_count', 'correct_patches_count', 'incorrect_patches_count']
    # for col in int_columns:
    #     final_df[col] = final_df[col].astype(int)

    try:
        final_df.to_csv(output_csv_path, index=False)
        print(f"\n分析结果已成功保存到: {output_csv_path}")
    except Exception as e:
        print(f"\n保存文件时出错: {e}")

    # 打印预览
    print("\n结果预览:")
    print(final_df)


def main():
    json_file1 = 'D:\\Projects\\python\\LLM\\correct_with_tests.json'
    json_file2 = 'D:\\Projects\\python\\LLM\\icse&llm_plausible_with_tests.json'

    output_dir = 'D:\\Projects\\python\\LLM\\'
    output_csv_file = 'total_pats.csv'
    pivot_csv_file = 'pivot_pats.csv'

    files_to_process = [json_file1, json_file2]

    final_df = extract_pats_from_files(files_to_process)
    if final_df is not None:
        print("提取结果预览 (前5行):")
        print(final_df.head())
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"\n创建输出目录: {output_dir}")
        full_output_path = os.path.join(output_dir, output_csv_file)
        try:
            final_df.to_csv(full_output_path, index=False)
            print(f"\n完整结果已成功保存到: {full_output_path}")
        except Exception as e:
            print(f"\n保存文件时出错: {e}")

        df_analyze(final_df, os.path.join(output_dir, pivot_csv_file))


if __name__ == '__main__':
    main()