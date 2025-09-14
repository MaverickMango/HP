import os
import pandas as pd
import system_prompt
import postprocess


def compute_predict(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            df = pd.read_csv(f)
        tn = len(df[(df['genuine'] == 'correct') & (df['verdict'] == 'correct')])
        fp = len(df[(df['genuine'] == 'correct') & (df['verdict'] == 'incorrect')])
        tp = len(df[(df['genuine'] == 'plausible') & (df['verdict'] == 'incorrect')])
        fn = len(df[(df['genuine'] == 'plausible') & (df['verdict'] == 'correct')])
        return tp, fp, tn, fn
    except Exception as e:
        print(f'文件读取错误：{str(e)}')
    return 0, 0, 0, 0


def compute_verdict(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            df = pd.read_csv(f)
        correct = df[df['verdict'] == 'correct'].shape[0]
        incorrect = df[df['verdict'] == 'incorrect'].shape[0]
        total_count = df.shape[0]
        assert correct + incorrect == total_count
        return correct, incorrect
    except Exception as e:
        print(f'文件读取错误：{str(e)}')
    return 0, 0


def compute_positive(file_path, threshold=0.85):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            df = pd.read_csv(f)
        count_above_threshold = df[df['confidence'] > threshold].shape[0]
        total_count = df.shape[0]
        # percentage_above_threshold = (count_above_threshold / total_count) * 100
        return count_above_threshold, total_count - count_above_threshold
    except Exception as e:
        print(f'文件读取错误：{str(e)}')
    return 0, 0


def compute_metrics(tp, fp, tn, fn):
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    balanced_acc = 1/2 * (recall + tn / (tn + fp))
    f1 = 2 * recall * precision / (recall + precision) if (recall + precision) > 0 else 0
    return recall, precision, accuracy, f1, balanced_acc


def compute_one_acca(result_root):
    file_name = 'result_data.csv'
    tp, fp, tn, fn = compute_predict(os.path.join(result_root, file_name))
    print(tp, fp, tn, fn)
    recall, precision, accuracy, f1, balanced= compute_metrics(tp=tp, fp=fp, tn=tn, fn=fn)
    print(f'过滤结果如下：')
    print(f'recall: {format(recall, '.2f')}')
    print(f'precision: {format(precision, '.2f')}')
    # print(f'accuracy: {format(accuracy, '.2f')}')
    print(f'f1 score: {format(f1, '.2f')}')
    print(f'balanced acc: {format(balanced, '.2f')}')


# def compute_one_acca(cres_root, pres_root):
#     file_name = 'result_data.csv'
#     correct_file_path = os.path.join(cres_root, file_name)
#     plausible_file_path = os.path.join(pres_root, file_name)
#     tp, fp = compute_verdict(correct_file_path)
#     fn, tn = compute_verdict(plausible_file_path)
#     recall, precision, accuracy, f1, balanced= compute_metrics(tp=tp, fp=fp, tn=tn, fn=fn)
#     print(f'过滤结果如下：')
#     print(f'recall: {format(recall, '.2f')}')
#     print(f'precision: {format(precision, '.2f')}')
#     # print(f'accuracy: {format(accuracy, '.2f')}')
#     print(f'f1 score: {format(f1, '.2f')}')
#     print(f'balanced acc: {format(balanced, '.2f')}')


def compute_one_filter(cres_root, pres_root, pattern=postprocess.pattern):
    file_name = 'result_data.csv'
    correct_file_path = os.path.join(cres_root, file_name)
    if not os.path.exists(correct_file_path):
        postprocess.get_result_csv(cres_root, pattern)
    plausible_file_path = os.path.join(pres_root, file_name)
    if not os.path.exists(plausible_file_path):
        postprocess.get_result_csv(pres_root, pattern)
    tn, fp = compute_verdict(correct_file_path)
    fn, tp = compute_verdict(plausible_file_path)
    if 0 in [tn, fp, fn, tp]:
        print("Warning：ZERO result found! skip this one.")
        return tp, tn, fp, fn, None, None, None, None, None
    recall, precision, accuracy, f1, balanced= compute_metrics(tp=tp, fp=fp, tn=tn, fn=fn)
    print(f'recall: {format(recall, '.2f')}')
    print(f'precision: {format(precision, '.2f')}')
    # print(f'accuracy: {format(accuracy, '.2f')}')
    print(f'f1 score: {format(f1, '.2f')}')
    print(f'balanced acc: {format(balanced, '.2f')}')
    return tp, tn, fp, fn, recall, precision, accuracy, f1, balanced


def compute_baselines(work_dir):
    baselines = ['cache', 'LLM4Correctness', 'quatrain'] #, 'ods', 'patchsim']
    for b in baselines:
        print(b)
        compute_one_acca(os.path.join(work_dir, b))


if __name__ == '__main__':
    # compute_one_acca('D:\\Projects\\python\\LLM\\baselines\\cache')
    # # apca3阈值为0.85的时候效果最好……
    # compute_baselines('D:\\Projects\\python\\LLM\\baselines\\')
    #
    recall, precision, accuracy, f1, balanced= compute_metrics(tp=0, fp=5, tn=53, fn=0)
    print(f'过滤结果如下：')
    print(f'recall: {format(recall, '.2f')}')
    print(f'precision: {format(precision, '.2f')}')
    # print(f'accuracy: {format(accuracy, '.2f')}')
    print(f'f1 score: {format(f1, '.2f')}')
    print(f'balanced acc: {format(balanced, '.2f')}')

    # # 计算单个变体
    # gpt4_preffix = 'apca7_'
    # cres = f'correct_with_classify_res'
    # pres = f'icse&llm_plausible_classify_res'
    # work_dir = 'gpt-4-1106-preview_nott'
    # compute_one_filter(f'{work_dir}/{cres}',
    #                    f'{work_dir}/{pres}',
    #                    postprocess.pattern)

    # # 计算模型对比
    # rows = []
    # for key in system_prompt.system_prompt.keys():
    #     cfn = cres
    #     pfn = pres
    #     if 'gpt' in key:
    #         cfn = gpt4_preffix + cres
    #         pfn = gpt4_preffix + pres
    #     cres_root = os.path.join(key, cfn)
    #     pres_root = os.path.join(key, pfn)
    #     print(f'过滤结果如下：')
    #     tp, tn, fp, fn, recall, precision, accuracy, f1, balanced = compute_one_filter(cres_root, pres_root)
    #     if None in [recall, precision, accuracy, f1, balanced]:
    #         continue
    #     rows.append([key, tp, tn, fp, fn, precision, recall, f1, balanced])
    # df = pd.DataFrame(rows)
    # df = df.round(2)
    # df.columns = ['Model', 'TP', 'TN', 'FP', 'FN', 'Precision', 'Recall', 'F1-score', 'Balanced-accuracy']
    # df.to_csv('models_results.csv', index=False)