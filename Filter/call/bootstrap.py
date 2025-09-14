import os
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, balanced_accuracy_score

import postprocess

# 设置随机种子以确保结果可重现
np.random.seed(42)

def split_verdict(file_path):
    df = pd.read_csv(file_path)
    correct_list = [0] * df[df['verdict'] == 'correct'].shape[0]
    incorrect_list = [1] * df[df['verdict'] == 'incorrect'].shape[0]
    return incorrect_list, correct_list


def read_results(cres_root, pres_root, pattern=postprocess.pattern):
    file_name = 'result_data.csv'
    correct_file_path = os.path.join(cres_root, file_name)
    if not os.path.exists(correct_file_path):
        postprocess.get_result_csv(cres_root, pattern)
    plausible_file_path = os.path.join(pres_root, file_name)
    if not os.path.exists(plausible_file_path):
        postprocess.get_result_csv(pres_root, pattern)
    tp_lst, fn_lst = split_verdict(plausible_file_path)
    tn_lst, fp_lst = split_verdict(correct_file_path)
    true = tp_lst + (1 - np.array(fn_lst)).tolist() + (1 - np.array(tn_lst)).tolist() + fp_lst
    pred = tp_lst + fn_lst + tn_lst + fp_lst
    # print(pred)
    return true, pred


if __name__ == '__main__':
    cres = f'correct_with_classify_res'
    pres = f'icse&llm_plausible_classify_res'
    work_dir = 'llama-2-70b'
    y_true, y_pred = read_results(f'{work_dir}/{cres}',
                       f'{work_dir}/{pres}',
                       postprocess.pattern)
    # exit()
    # 将真实标签和预测标签组合成总体预测集
    predictions = list(zip(y_true, y_pred))
    n = len(predictions)  # 样本数量

    # 初始化存储指标的数组
    n_iterations = 5000
    f1_scores = np.zeros(n_iterations)
    balanced_accuracies = np.zeros(n_iterations)

    # 重采样并计算指标
    for i in range(n_iterations):
        # 有放回地随机抽样，创建自举样本
        indices = np.random.choice(n, size=n, replace=True)
        bootstrap_sample = [predictions[idx] for idx in indices]
        # 分离真实标签和预测标签
        y_true_bootstrap = np.array([sample[0] for sample in bootstrap_sample])
        y_pred_bootstrap = np.array([sample[1] for sample in bootstrap_sample])

        # 计算F1分数
        f1_scores[i] = f1_score(y_true_bootstrap, y_pred_bootstrap, zero_division=0)

        # 计算平衡准确率
        balanced_accuracies[i] = balanced_accuracy_score(y_true_bootstrap, y_pred_bootstrap)

    # 步骤5: 确定置信区间
    # 对估计值进行排序
    f1_scores_sorted = np.sort(f1_scores)
    balanced_accuracies_sorted = np.sort(balanced_accuracies)

    # 计算2.5%和97.5%分位数
    alpha = 0.05
    lower_idx = int(n_iterations * alpha / 2)
    upper_idx = int(n_iterations * (1 - alpha / 2))

    f1_ci = (f1_scores_sorted[lower_idx], f1_scores_sorted[upper_idx])
    balanced_accuracy_ci = (balanced_accuracies_sorted[lower_idx], balanced_accuracies_sorted[upper_idx])

    # 输出结果
    print(f"F1分数95%置信区间: [{f1_ci[0]:.4f}, {f1_ci[1]:.4f}]")
    print(f"平衡准确率95%置信区间: [{balanced_accuracy_ci[0]:.4f}, {balanced_accuracy_ci[1]:.4f}]")

    # 可选: 输出原始指标值
    original_f1 = f1_score(y_true, y_pred)
    original_balanced_accuracy = balanced_accuracy_score(y_true, y_pred)
    print(f"原始F1分数: {original_f1:.4f}")
    print(f"原始平衡准确率: {original_balanced_accuracy:.4f}")
