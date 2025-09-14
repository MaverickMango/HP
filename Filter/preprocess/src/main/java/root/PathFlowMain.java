package root;

import root.util.CommandSummary;
import root.util.FileUtils;

import java.util.List;

public class PathFlowMain extends Main{

    public static void main(String[] args) {
        /*
        /home/liumengjiao/Desktop/CI/bugs/
        /home/liumengjiao/Desktop/CI/Benchmark_py/generation/info/patches_inputs.csv
        /home/liumengjiao/Desktop/CI/D4JPatches/patches_plausible
        /home/liumengjiao/IdeaProjects/PDA-trace/info/
         */
        String location = args[0]; // "/home/liumengjiao/Desktop/CI/bugs/";
        String info = args[1]; // "/home/liumengjiao/Desktop/CI/Benchmark_py/generation/info/patches_inputs.csv";
        String patchesRootDir = args[2];
        String sliceRoot = args[3];///home/liumengjiao/IdeaProjects/PDA-trace/info/
        List<List<String>> lists = FileUtils.readCsv(info, true);
        CommandSummary cs;
        for (int i = 0; i < lists.size(); i ++) {//closure133-31,math50-46,math-105-91,lang51-35,closure64-14
            List<String> strings  = lists.get(i);
            cs = setInputs(location, strings);
            String patchesDir = getPatchDirByBug(strings.get(0), patchesRootDir);
            cs.append("-patchesDir", patchesDir);
            cs.append("-sliceRoot", sliceRoot);
            boolean res = execute(cs);
            i = lists.size();
        }
    }
}
