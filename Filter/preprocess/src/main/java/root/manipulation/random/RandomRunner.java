package root.manipulation.random;

import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.utils.Pair;
import root.ProjectPreparation;
import root.entities.Patch;
import root.entities.Stats;
import root.generation.entities.Input;
import root.generation.entities.Skeleton;
import root.generation.transformation.Runner;
import root.util.ConfigurationProperties;
import root.util.FileUtils;
import root.util.PatchHelper;
import root.util.TimeUtil;

import java.io.File;
import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class RandomRunner extends Runner {

    public RandomRunner(ProjectPreparation projectPreparation) {
        super(projectPreparation);
        this.creatorHelper = new RandomCreatorHelper(50);
    }

    @Override
    public void mutateTests(Skeleton skeleton) {
        try {
            List<Input> newInputs = new ArrayList<>();
            List<Input> inputs = skeleton.getInputs();
            logger.info("Mutating test inputs... total inputs num: " + inputs.size());
            for (Input input : inputs) {
                logger.info("getting mutants...");
                List<Pair<Expression, ? extends LiteralExpr>> inputMutants = creatorHelper.getInputMutants(input);
                logger.info("transforming...");
                List<Input> tmp = constructHelper.transformInput(input, inputMutants);
                newInputs.addAll(tmp);
//            skeleton.addInput(input);
            }
            logger.info("Building new tests...");
            // 保存新生成的测试到对应的测试类文件里
            CompilationUnit[] compilationUnits = constructHelper.buildCompetitiveTests(skeleton, newInputs);
        } catch (Exception e) {
            logger.error(e.getMessage());
        }
    }

    ExecutorService executionService, patchValidateService;
    int generation_run = 0;

    @Override
    public boolean run() {
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
            logger.info("----------Start patch validation----------");
            startDate = new Date();
            allCorrect = validate(sks);
            logger.info("End patches validation --------------------");
            validationSeconds += TimeUtil.deltaInSeconds(startDate);
            if (!allCorrect || generationSeconds + validationSeconds >= total) {
                break;
            }
//            try {
//                executionService.shutdown();
//                if (!executionService.awaitTermination(1, TimeUnit.MINUTES)) {
//                    logger.info("Error found: Could not finish in 1 minute for " + sks.size() + " Test(s)'s mutation.");
//                    executionService.shutdownNow();
//                    if (!executionService.awaitTermination(10, TimeUnit.SECONDS)) {
//                        logger.error("Thread not terminated.");
//                    }
//                }
//            } catch (InterruptedException e) {
//                Thread.currentThread().interrupt();
//                System.err.println("Mutate thread pool interrupted: " + e.getMessage());
//            }
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

    @Override
    public boolean validate(List<Skeleton> mutateRes) {
        logger.info("Processing patches validation --------------------");
        StringBuilder clzNames = new StringBuilder();
        for (Skeleton skeleton :mutateRes) {
            clzNames.append(skeleton.getClazzName()).append(" ");
        }
        //在历史版本执行
        logger.info("Executing tests in original version.");
        PatchHelper.tests4Clz(clzNames.toString(), true);
        //复制历史版本执行结果
        String newOraclePath = PatchHelper.testTarget + File.separator
                + Runner.orgTestResultInfix + File.separator
                + ConfigurationProperties.getProperty("generation_run") + "_generation.txt";
        FileUtils.copy(new File(PatchHelper.oracleOutputs), new File(newOraclePath));
        FileUtils.removeFile(PatchHelper.oracleOutputs);
        List<String> orgRes = FileUtils.readEachLine(newOraclePath);

        Iterator<Patch> iterator = projectPreparation.patches.iterator();
        AtomicInteger count = new AtomicInteger();
        List<String>[] patchesRess = new List[projectPreparation.patches.size()];
        /*
         * 单线程执行
         */
        while (iterator.hasNext()) {
            Patch patch = iterator.next();
            boolean res = PatchHelper.patchValidate(patch, clzNames.toString());
            patchesRess[count.get()] = new ArrayList<>();
            count.getAndIncrement();
            if (!res) {
                continue;
            }
            //复制补丁版本测试结果
            File dstFile = new File(PatchHelper.testTarget + File.separator + Runner.patTestResultInfix
                    + File.separator + patch.getName()
                    + File.separator + ConfigurationProperties.getProperty("generation_run") + "_generation.txt");
            FileUtils.copy(new File(PatchHelper.oracleOutputs), dstFile);
            FileUtils.removeFile(PatchHelper.oracleOutputs);
            List<String> patchRes = FileUtils.readEachLine(dstFile.getAbsolutePath());
            patchesRess[count.get()] = patchRes;// 这里执行不成功的话Ress就有可能为空!
        }
        /*
         * 多线程执行
         */
//        while (iterator.hasNext()) {
//            Patch patch = iterator.next();
//            Runnable task = () -> {
//                String outputFile = PatchHelper.oracleOutputs.replace("_org", "_pat");
//                (new File(outputFile)).delete();
//                boolean res = PatchHelper.patchValidate(patch, clzNames.toString());
//                if (!res) {
//                    return;
//                }
//                //收集测试结果
//                List<String> patchRes = FileUtils.readEachLine(outputFile);
//                patchesRess[count.get()] = patchRes;
//                count.getAndIncrement();
//            };
//            patchValidateService.submit(task);
//        }
        //收集结果
        return PatchHelper.setPatchResultStats(patchesRess, orgRes);
    }

}
