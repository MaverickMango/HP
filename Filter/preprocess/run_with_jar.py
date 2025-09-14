import os
import sys
import csv

jar_path = 'Desktop/CI/Benchmark/out/artifacts/Benchmark_jar/Benchmark.jar'
patches_dir_root = 'Desktop/CI/D4JPatches/patches_correct:' \
                   'Desktop/CI/D4JPatches/patches_plausible'
bug_location = 'Desktop/CI/bugs/{proj}/{bug_name}_buggy'
resultOutput = 'Desktop/CI/Benchmark_py/generation/run/res_in_turn/'

bug_info_path = '../info/patches_inputs.csv'
def get_patch_list() :
    with open(bug_info_path, 'r') as f:
        csv_reader = csv.DictReader(f)
        bug_info_list = [item for item in csv_reader]
    return bug_info_list


if __name__ == '__main__':
    """
    
        String bugName, srcJavaDir, srcTestDir, binJavaDir, binTestDir, testInfos, projectCP, originalCommit, cleaned, complianceLevel;
        bugName = strings.get(5);
        srcJavaDir = strings.get(1);
        srcTestDir = strings.get(2);
        binJavaDir = strings.get(3);
        binTestDir = strings.get(4);
        testInfos = strings.get(5);
        projectCP = strings.get(6);
        originalCommit = strings.get(7);
        complianceLevel = strings.get(8);
        cleaned = strings.get(9);
        cs.append("-proj", bugName.split("_")[5]);
        cs.append("-id", bugName.split("_")[1]);
        cs.append("-location", location + bugName + "_bug");
        cs.append("-srcJavaDir", srcJavaDir);
        cs.append("-srcTestDir", srcTestDir);
        cs.append("-binJavaDir", binJavaDir);
        cs.append("-binTestDir", binTestDir);
        cs.append("-testInfos", testInfos);
        cs.append("-dependencies", projectCP);
        cs.append("-originalCommit", originalCommit);
        cs.append("-complianceLevel", "1.6");
        cs.append("-patchesDir", patchesDir);
    """
    count = 0
    bug_info_list = get_patch_list()
    print('total bug: ' + str(len(bug_info_list)))
    for bug_info in bug_info_list:
        bugName = bug_info['bug_name']
        proj = bugName.split('_')[0]
        id = bugName.split('_')[1]
        location = bug_location.format(proj=proj,bug_name=bugName)
        srcJavaDir = bug_info['srcJavaDir']
        srcTestDir = bug_info['srcTestDir']
        binJavaDir = bug_info['binJavaDir']
        binTestDir = bug_info['binTestDir']
        testInfos = bug_info['trigger_test_class_function_line']
        projectCP = bug_info['projectCP']
        originalCommit = bug_info['originalCommit']
        complianceLevel = '1.8'
        if not bug_info['cleaned']:
            continue
        dirs_root = patches_dir_root.split(":")
        dirs = ''
        for root in dirs_root:
            root += "/" + proj + "/" + bugName + "/"
            if os.path.exists(root):
                dirs += ":" + root
        if dirs == '':
            continue

        count += 1
        print(f'executing bug {bugName}, {count} in {len(bug_info_list)}')
        log_path = resultOutput + bugName
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        cmd = f'/usr/local/lib/jdk-11.0.19/bin/java -jar {jar_path} root.Main ' \
                f'-proj {proj} -id {id} -location {location} ' \
                f'-srcJavaDir {srcJavaDir} -srcTestDir {srcTestDir} ' \
                f'-binJavaDir {binJavaDir} -binTestDir {binTestDir} ' \
                f'-testInfos {testInfos} -dependencies {projectCP} ' \
                f'-originalCommit {originalCommit} -complianceLevel {complianceLevel} ' \
                f'-patchesDir {dirs[1:]} -resultOutput {resultOutput}'#
        # cmd = f'/usr/local/lib/jdk-11.0.19/bin/java -jar {jar_path} root.generation.TestInputMutateForBugsMain ' \
        #         f'-proj {proj} -id {id} -location {location} ' \
        #         f'-srcJavaDir {srcJavaDir} -srcTestDir {srcTestDir} ' \
        #         f'-binJavaDir {binJavaDir} -binTestDir {binTestDir} ' \
        #         f'-testInfos {testInfos} -dependencies {projectCP} ' \
        #         f'-originalCommit {originalCommit} -complianceLevel {complianceLevel} ' \
        #         f'-patchesDir {dirs[1:]} -resultOutput {resultOutput} > {log_path}/PatchPredict.log 2>&1'#
        # print(cmd)
        os.system(cmd)
        with open(f'{log_path}/cmd.txt', 'w') as f:
            f.write(cmd)

        cmd = f'mv ./PatchPredict.log {log_path}/'
        os.system(cmd)
    print('total executed: ' + str(count))