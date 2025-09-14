import os,sys
import json


def process(target_dir, ouput_file):
    """
    根据stats文件分析运行结果
    :param target_dir: 补丁过滤运行结果根目录
    :param ouput_file: 分析结果输出文件
    :return: null
    """
    root_of_results = os.path.abspath(target_dir)
    result = {"bugs": {}, "total_avg": {}, "total_res": {}}
    stat_count = 0
    total = 0
    no_output = 0
    error_count = 0
    total_genuine_correct = 0
    total_genuine_plausible = 0
    total_correct_filtered = 0
    total_correct_not_filtered = 0
    total_plausible_filtered = 0
    total_plausible_not_filtered = 0
    total_patch_count = 0

    for folder in os.listdir(root_of_results):
        folder_path = os.path.join(root_of_results, folder)
        if os.path.isdir(folder_path):
            if not os.listdir(folder_path):
                continue
            total += 1
            stat_path = os.path.join(folder_path, "stats")
            if not os.path.exists(stat_path):
                result["bugs"][folder] = "NO_OUTPUT"
                no_output += 1
            else:
                try:
                    with open(stat_path, 'r') as f:
                        stat_data = json.load(f)
                        result["bugs"][folder] = {}
                        stat_count += 1

                        for key, value in stat_data.items():
                            if key == "generalStats":
                                for k, v in stat_data[key].items():
                                    result["total_avg"][k] = result["total_avg"].get(k, 0) + v
                            if key == "patchStats":
                                # result["total_res"]
                                # 按正确补丁和错误补丁分类,统计不同类别补丁对应的过滤结果是什么,以及总共有多少补丁
                                genuine_correct = 0
                                genuine_plausible = 0
                                correct_filtered = 0
                                correct_not_filtered = 0
                                plausible_filtered = 0
                                plausible_not_filtered = 0
                                patch_count = 0
                                result["bugs"][folder]["genuine_correct"] = {}
                                result["bugs"][folder]["genuine_plausible"] = {}
                                # for patch, patch_stat in value.items():
                                for k, v in value.items():  # key是补丁的名字
                                    patch_count += 1
                                    if v["GENUINE"] == "correct":
                                        genuine_correct += 1
                                        result["bugs"][folder]["genuine_correct"]["count"] = \
                                            result["bugs"][folder]["genuine_correct"].get("count", 0) + 1

                                        if "CORRECTNESS" in v and v["CORRECTNESS"] == "correct":
                                            correct_not_filtered += 1
                                            result["bugs"][folder]["genuine_correct"]["not_filtered"] = \
                                                result["bugs"][folder]["genuine_correct"].get(
                                                "not_filtered", 0) + 1
                                        else:
                                            correct_filtered += 1
                                            result["bugs"][folder]["genuine_correct"]["filtered"] = \
                                                result["bugs"][folder]["genuine_correct"].get("filtered", 0) + 1
                                    else:
                                        genuine_plausible += 1
                                        result["bugs"][folder]["genuine_plausible"]["count"] = \
                                            result["bugs"][folder]["genuine_plausible"].get("count", 0) + 1

                                        if "CORRECTNESS" in v and v["CORRECTNESS"] == "correct":
                                            plausible_not_filtered += 1
                                            result["bugs"][folder]["genuine_correct"]["not_filtered"] = \
                                                result["bugs"][folder]["genuine_correct"].get(
                                                "not_filtered", 0) + 1
                                        else:
                                            plausible_filtered += 1
                                            result["bugs"][folder]["genuine_plausible"]["filtered"] = \
                                                result["bugs"][folder]["genuine_plausible"].get("filtered", 0) + 1

                                result["bugs"][folder]["patch_count"] = patch_count

                                total_patch_count += patch_count
                                total_genuine_correct += genuine_correct
                                total_genuine_plausible += genuine_plausible
                                total_correct_not_filtered += correct_not_filtered
                                total_correct_filtered += correct_filtered
                                total_plausible_not_filtered += plausible_not_filtered
                                total_plausible_filtered += plausible_filtered
                except (json.JSONDecodeError, IOError):
                    result["bugs"][folder] = "ERROR_FILE"
                    error_count += 1
    for key, value in result["total_avg"].items():
        result["total_avg"][key] = round(value / stat_count, 2)

    result["total_res"]["total_run"] = total  # total run
    result["total_res"]["error_run"] = no_output  # without stat file
    result["total_res"]["correct_run"] = stat_count  # correctly output stat file
    result["total_res"]["total_patch"] = total_patch_count
    result["total_res"]["correct_patch"] = total_genuine_correct
    result["total_res"]["plausible_patch"] = total_genuine_plausible
    result["total_res"]["correct_not_filtered"] = total_correct_not_filtered
    result["total_res"]["correct_filtered"] = total_correct_filtered
    result["total_res"]["plausible_not_filtered"] = total_plausible_not_filtered
    result["total_res"]["plausible_filtered"] = total_plausible_filtered

    with open(ouput_file, 'w') as output:
        json.dump(result, output, indent=4)


if __name__ == "__main__":
    working_dir = "res_in_turn/"
    process(working_dir, "./output_result.json")