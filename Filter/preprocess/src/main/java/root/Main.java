package root;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import root.entities.*;
import root.generation.transformation.Runner;
import root.manipulation.random.RandomFuzzRunner;
import root.manipulation.random.RandomRunner;
import root.util.*;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

public class Main extends AbstractMain {

    private static final Logger logger = LoggerFactory.getLogger(Main.class);

    public static CommandSummary setInputs(String location, List<String> strings) {
        CommandSummary cs = new CommandSummary();
        String bugName, srcJavaDir, srcTestDir, binJavaDir, binTestDir, testInfos, projectCP, originalCommit, cleaned, complianceLevel;
        bugName = strings.get(0);
        srcJavaDir = strings.get(1);
        srcTestDir = strings.get(2);
        binJavaDir = strings.get(3);
        binTestDir = strings.get(4);
        testInfos = strings.get(5);
        projectCP = strings.get(6);
        originalCommit = strings.get(7);
//        complianceLevel = strings.get(8);
        cleaned = strings.get(8);
        String proj = bugName.split("_")[0];
        Path path = Paths.get(location).toAbsolutePath();
        location = path.resolve(proj + File.separator + bugName + "_buggy").normalize().toString();
        cs.append("-proj", proj);
        cs.append("-id", bugName.split("_")[1]);
        cs.append("-location", location);
        cs.append("-srcJavaDir", srcJavaDir);
        cs.append("-srcTestDir", srcTestDir);
        cs.append("-binJavaDir", binJavaDir);
        cs.append("-binTestDir", binTestDir);
        cs.append("-testInfos", testInfos);
        cs.append("-dependencies", projectCP);
        cs.append("-originalCommit", originalCommit);
//        cs.append("-complianceLevel", "1.6");
        return cs;
    }

    public static void main(String[] args) {
//        String sliceRoot = args[3];//"/home/liumengjiao/Desktop/CI/Benchmark_py/slice/results/";
//        logger.info("sliceRoot: " + sliceRoot);
        CommandSummary cs = new CommandSummary(args);
        boolean res = execute(cs);
    }

    static boolean execute(CommandSummary cs) {
        logger.info("---------Start Initialization----------");
        Main main = new Main();
        ProjectPreparation projectPreparation = main.initialize(cs.flat());
        if (projectPreparation == null) {
            return false;
        }
        long seconds = TimeUtil.deltaInSeconds(main.bornTime);
        Stats.getCurrentStats().addGeneralStat(Stats.General.INITIALIZATION_TIME, seconds);
//        logger.info("Initialization end with time cost " + seconds + "s");

        Date startDate = new Date();
        logger.info("---------Start patch filtering----------");
        Runner runner = new RandomFuzzRunner(projectPreparation);
        boolean allCorrect = runner.run();

        projectPreparation.after();

        String resultOutput = ConfigurationProperties.getProperty("resultOutput") + File.separator
                + projectPreparation.bug.getBugName() + File.separator + "stats";
        FileUtils.writeToFile(Stats.getCurrentStats().toString(), resultOutput, false);
        long totalSeconds = TimeUtil.deltaInSeconds(main.bornTime);
        Stats.getCurrentStats().addGeneralStat(Stats.General.TOTAL_TIME, totalSeconds);
        logger.info("Finish with total running time: " + totalSeconds + "s");
        return allCorrect;
    }

    static String getPatchDirByBug(String bugName, String patchesRootDir) {
        String[] split = bugName.split("_");
        String proj = split[0];
        String id = split[1];
        String patchDir = patchesRootDir + File.separator + proj + File.separator + proj + "_"+ id;
        return patchDir;
    }
}
