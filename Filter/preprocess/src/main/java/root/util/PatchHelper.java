package root.util;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import root.analysis.ASTExtractor;
import root.analysis.parser.AbstractASTParser;
import root.entities.Stats;
import root.entities.ci.BugRepository;
import root.entities.Patch;
import root.generation.transformation.Runner;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

public class PatchHelper {

    private final static Logger logger = LoggerFactory.getLogger(PatchHelper.class);
    public static String oracleOutputs;
    public static String testTarget;
//    public static String resOutput;
    public static root.analysis.ASTExtractor ASTExtractor;
    public static BugRepository patchRepository;
    public static String oracleFileName = "generatedOracles.txt";

    public static void initialization(BugRepository pat, AbstractASTParser parser) {
        String bugName = Runner.bugRepository.getBug().getBugName();
        //save the generatedOracle file.
        testTarget = ConfigurationProperties.getProperty("resultOutput") + File.separator
                + bugName + File.separator + "generatedTestResults" + File.separator;
        File target = new File(testTarget);
        FileUtils.removeFile(target);
        target.mkdirs();
//        resOutput = ConfigurationProperties.getProperty("resultOutput") + File.separator
//                + bugName + File.separator + "result" + File.separator;
        ASTExtractor = new ASTExtractor(parser);
        patchRepository = pat;
//        patchRepository.switchToBug();
//        patchRepository.compile();
        oracleOutputs = testTarget + oracleFileName;
    }

    public static boolean patchValidate(Patch patch, String clzNames) {
        boolean res = patchRepository.applyPatch(patch);
        if (!res) {
            logger.error("Error occurred when applying patch " + patch.getName());
            return res;
        }
        //original version just run once outside this method;
        //for one patch apply all the tests and run.
        logger.info("Applying patch: " + patch);
        res = tests4Clz(clzNames, false);//只代表执行是否成功，测试没有编译错误就应该全通过
//        String correctness = res ? "correct" : "incorrect";
//        logger.info("Patch correctness : " + correctness + " for " + patch.getName());
//        String content = patch.getPatchAbsPath() + "#" + correctness + "\n";
//        FileUtils.writeToFile(content, resOutput, true);
        patchRepository.restore(patch);
        return res;
    }

    public static boolean tests4Clz(String testClass, boolean isOracle) {
        BugRepository repo = isOracle ? Runner.orgRepository : PatchHelper.patchRepository;
        List<String> r = repo.testRelevantWithRes(testClass);
        if (r.isEmpty() || !r.get(0).equals("0")) {// todo 这里执行了所有的测试而不仅仅是指定的类！！！
            logger.error("Test execution error! :\n" + FileUtils.getStrOfIterable(r, "\n"));
            return false;
        }
        return true;
    }

    public static List<String>[] processLists(List<String> patchRes, List<String> oracles) {
        // 排序X和N中的每个List
        Collections.sort(oracles);
        Collections.sort(patchRes);

        // 创建结果数组
        List<String>[] result = new List[2];
        result[0] = new ArrayList<>();

        // 处理每个X中的元素
        for (String xElement : oracles) {
            if (xElement.isEmpty()) {
                continue;
            }
            String[] xParts = xElement.split("::");
            String xPrefix = String.join("::", Arrays.copyOf(xParts, xParts.length - 1));
            String xValue = xParts[xParts.length - 1];

            result[1] = new ArrayList<>();
            List<String> collect = patchRes.stream().filter(l -> l.startsWith(xPrefix + "::")).collect(Collectors.toList());
            if (collect.isEmpty()) {
//                result[0].add(xElement);
                //todo 返回没有在patch版本执行成功的测试名
//                System.err.println(xElement);
                continue;
            }
            String nElement = collect.get(0);
            if (!nElement.endsWith(xValue)) {
                result[0].add(xElement);
                result[1].add(nElement);
            }
        }

        return result;
    }


    public static List<String>[] compareTwoVersionsResults(List<String>[] patchesReses, List<String> oracles) {
        // 创建结果数组,数组中的每个元素表示对应编号的patch中org版本和pat版本表现不一致时候的测试结果
        List<String>[] result = new List[patchesReses.length];
        if (result.length == 0) {
            return result;
        }

        // 排序X和N中的每个List
        Collections.sort(oracles);
        for (List<String> list : patchesReses) {
            Collections.sort(list);
        }

        // 处理每个X中的元素
        for (int i = 0; i < oracles.size(); i++) {
            String xElement = oracles.get(i);
            if (xElement.isEmpty()) {
                continue;
            }
            String[] xParts = xElement.split("::");
            String xPrefix = String.join("::", Arrays.copyOf(xParts, xParts.length - 1));
            String xValue = xParts[xParts.length - 1];

            for (int j = 0; j < patchesReses.length; j++) {
                if (result[j] == null) {
                    result[j] = new ArrayList<>();
                }
                List<String> results = patchesReses[j];
                List<String> collect = results.stream().filter(l -> l.startsWith(xPrefix + "::")).collect(Collectors.toList());
                if (collect.isEmpty()) {
                    result[j].add("NO_RUN#" + xPrefix);//返回没有在patch版本执行成功的测试名
                    System.err.println(xElement);
                    continue;
                }
                String nElement = collect.get(0);
                if (!nElement.endsWith(xValue)) {
                    //和oracles中的测试结果表现不一致的
                    result[j].add(xElement + "#" + nElement);
                }
            }
        }

        return result;
    }

    public static boolean setPatchResultStats(List<String>[] patchesReses, List<String> oracles) {
        List<String>[] lists = PatchHelper.compareTwoVersionsResults(patchesReses, oracles);
        for (int i = 0; i < lists.length; i ++) {
            List<String> list  = lists[i];
            Stats.getCurrentStats().addPatchStat(String.valueOf(i), Stats.Patch_stat.CORRECTNESS, "correct");
            if (list == null) {//为空的时候是没有在历史版本执行成功
                Stats.getCurrentStats().addPatchStat(String.valueOf(i), Stats.Patch_stat.RESULT, "TEST_ERROR#NO_ORI_ORACLES");
                return false; //历史版本有误所以直接返回错误
            }
            if (list.isEmpty()) {
                Stats.getCurrentStats().addPatchStat(String.valueOf(i), Stats.Patch_stat.RESULT, "TEST_EQUAL");
                return true; //两个版本测试表现一致继续进行下一轮
            }
            List<String> no_ress = new ArrayList<>();
            List<String> diff_ress = new ArrayList<>();
            for (String res: list) {
                if (res.contains("NO_RUN")) {
                    no_ress.add(res);
                } else {
                    diff_ress.add(res);
                }
            }
            if (!diff_ress.isEmpty()) {
                logger.info("Difference test result in pat {}", i);
                Stats.getCurrentStats().addPatchStat(String.valueOf(i), Stats.Patch_stat.RESULT, "TEST_DIFF#" + String.join("::", diff_ress));
                Stats.getCurrentStats().addPatchStat(String.valueOf(i), Stats.Patch_stat.CORRECTNESS, "incorrect");
                return false;
            } else {
                Stats.getCurrentStats().addPatchStat(String.valueOf(i), Stats.Patch_stat.RESULT, "TEST_ERROR#" + String.join("::", no_ress));
            }
        }
        return true;
    }

//    public static boolean validate(Patch patch, List<Skeleton> skeletons) {
//        boolean res = patchRepository.applyPatch(patch);
//        if (!res) {
//            logger.error("Error occurred when applying patch " + patch.getName());
//            return res;
//        }
//        logger.info("Applying patch: " + patch);
//        for (Skeleton skeleton :skeletons) {
//            //copy oracle file
//            FileUtils.copy(new File(skeleton.getOracleFilePath(true)), new File(testTarget));
//            List<String> failed = skeleton.runGeneratedTests(skeleton.getGeneratedMethods());
//            if (failed == null) {
//                logger.info("Test execution error in patched version!");
//                continue;
//            }
//            res &= failed.isEmpty();//failed为空贼说明没有失败测试，是一个正确的补丁。
//        }
//        String correctness = res ? "correct" : "incorrect";
//        logger.info("Patch correctness : " + correctness + " for " + patch.getName());
//        String content = patch.getPatchAbsPath() + "#" + correctness + "\n";
//        FileUtils.writeToFile(content, resOutput, true);
//        return res;
//    }
}
