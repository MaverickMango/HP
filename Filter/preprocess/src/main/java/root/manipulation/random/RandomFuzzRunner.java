package root.manipulation.random;

import root.ProjectPreparation;
import root.analysis.slicer.Slicer;
import root.diff.DiffExtractor;
import root.entities.*;
import root.generation.entities.Skeleton;
import root.util.ConfigurationProperties;
import root.util.TimeUtil;

import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

public class RandomFuzzRunner extends RandomRunner {

    Slicer slicer;
    Map<String, List<ExecutionPathInMth>> paths;

    public RandomFuzzRunner(ProjectPreparation projectPreparation) {
        super(projectPreparation);
        this.creatorHelper = new RandomCreatorHelper(50);
        slicer = getSlicer();
        logger.info("...Parsing test traces");
        paths = slicingPaths();//每个覆盖函数对应的执行路径
        constructConstraints();
    }

    @Override
    public boolean run() {
        if (ConfigurationProperties.getPropertyBool("pathFlowOnly")) {
            return true;
        }
        boolean allCorrect = true;
        Date startDate = new Date();
        List<Skeleton> sks = getTestsSkeletons();
        if (sks.isEmpty()) {
            return false;
        }
        long generationSeconds = 0;
        long validationSeconds = 0;
        double total = ConfigurationProperties.getPropertyDouble("totalTimeoutSecond");
        logger.info("----------Start test generation----------");
//        executionService = Executors.newFixedThreadPool(10);
        while (true) {
            generation_run = ConfigurationProperties.getPropertyInt("generation_run");
            ConfigurationProperties.setProperty("generation_run", String.valueOf(++ generation_run));
//            patchValidateService = Executors.newFixedThreadPool(10);
            for (Skeleton skeleton: sks) {
                logger.info("Current skeleton is: " + skeleton.getClazzName());
                logger.info("Generation " + generation_run);
                mutateTests(skeleton);
            }
            generationSeconds += TimeUtil.deltaInSeconds(startDate);
//            logger.info("----------Start patch validation----------");
//            startDate = new Date();
//            allCorrect = validate(sks);
//            logger.info("End patches validation --------------------");
            validationSeconds += TimeUtil.deltaInSeconds(startDate);
            if (!allCorrect || generationSeconds + validationSeconds >= total) {
                break;
            }
        }
        AtomicInteger cnt = new AtomicInteger();
        sks.forEach(s -> cnt.addAndGet(s.getGeneratedMethods().size()));
        Stats.getCurrentStats().addGeneralStat(Stats.General.GENERATED_TESTS, cnt);
        Stats.getCurrentStats().addGeneralStat(Stats.General.GENERATION_TIME, generationSeconds);
//        logger.info("Test generation end with time cost " + seconds + "s");
        Stats.getCurrentStats().addGeneralStat(Stats.General.VALIDATION_TIME, validationSeconds);
//        logger.info("Patch validation end with time cost " + seconds + "s");
        return allCorrect;
    }

//    @Override
//    public Map<String, List<String>> getTestsByClazz() {
//        slicer = getSlicer();
//        logger.info("...Parsing test traces");
//        paths = slicingPaths();//每个覆盖函数对应的执行路径
//        return constructHelper.getTestInfos(paths.keySet().toArray(new String[paths.keySet().size()]));
//    }

    @Override
    public void mutateTests(Skeleton skeleton) {
        super.mutateTests(skeleton);
    }

    @Override
    public boolean validate(List<Skeleton> mutateRes) {
        return super.validate(mutateRes);
    }

    private Slicer getSlicer() {
        if (slicer != null) {
            return slicer;
        }
        logger.info("Invoking slicer for analysis");
        String m = ConfigurationProperties.getProperty("slicingMode");
        Slicer.MODE mode;
        switch (m.toLowerCase()) {
            case "all":
                mode = Slicer.MODE.ALL;
                break;
            case "fault":
                mode = Slicer.MODE.FAULT;
                break;
            default:
                mode = Slicer.MODE.DIFF;
        }
        Stats.getCurrentStats().addGeneralStat(Stats.General.SLICING_MODE, mode);
        return new Slicer(projectPreparation.srcJavaDir, projectPreparation.srcTestDir, projectPreparation.sliceLog, mode);
    }

    private List<Difference> diffExtraction() {
        /*
         * 1. 提取differences中的差异变量DiffExprs
         * 2. 寻找DiffExprs和input之间的关系
         *      =》a. <s>获取调用图</s> 获取失败测试的trace
         *        b. <s>静态分析每个函数内部的依赖关系</s> 根据trace进行切片
         *        c. 在切片的同时构造其依赖的条件表达式和变量传播关系
         */
        List<Difference> differences = new ArrayList<>();
        Date startDate = new Date();
        DiffExtractor diffExtractor = new DiffExtractor();
        List<Patch> patches = projectPreparation.patches;
        if (patches == null) {
            return differences;
        }
        for (Patch patch :patches) {
            Difference difference = diffExtractor.getDifferenceForPatch(patch);
            differences.add(difference);
            Stats.getCurrentStats().addPatchStat(patch.getName(), Stats.Patch_stat.DIFF, difference);
        }
        long seconds = TimeUtil.deltaInSeconds(startDate);
        Stats.getCurrentStats().addGeneralStat(Stats.General.DIFF_TIME, seconds);
        return differences;
    }

    private Map<String, List<ExecutionPathInMth>> slicingPaths() {
        if (paths != null) {
            return paths;
        }
        return slicer.traceParser();
    }

    private List<PathFlow> constructConstraints() {
        List<Difference> differences = null;
        if (slicer.mode.equals(Slicer.MODE.DIFF)) {
             differences = diffExtraction();
            if (differences.isEmpty()) {
                return new ArrayList<>();
            }
        }
        try {
            List<ExecutionPathInMth> next = paths.values().iterator().next();//只选取第一个测试来收集路径信息
            logger.info("...Analyse dependencies of traces");
            List<PathFlow> pathFlows = slicer.dependencyAnalysis(differences, next);

            Set<Object> constants = new HashSet<>();
            for (PathFlow pathFlow: pathFlows) {
                constants.addAll(pathFlow.getConstants());
            }

            return pathFlows;
        } catch (Exception e) {
            logger.error("Error occurred when analyse dependencies! " + e.getMessage());
            e.printStackTrace();
        }
        return new ArrayList<>();
    }
}
