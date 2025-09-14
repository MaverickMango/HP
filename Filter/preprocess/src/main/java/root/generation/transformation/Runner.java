package root.generation.transformation;

import com.github.javaparser.ast.CompilationUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import root.ProjectPreparation;
import root.entities.ci.BugRepository;
import root.entities.ci.BugWithHistory;
import root.execution.IPatchValidator;
import root.generation.entities.Input;
import root.generation.entities.Skeleton;
import root.analysis.parser.AbstractASTParser;
import root.analysis.ASTExtractor;
import root.util.ConfigurationProperties;
import root.util.FileUtils;

import java.io.File;
import java.util.*;

public abstract class Runner implements IPatchValidator {

    public Logger logger = LoggerFactory.getLogger(this.getClass());
    public static ConstructHelper constructHelper;
    public static BugRepository bugRepository;
    public static BugRepository orgRepository;
    public static String generationOutput;
    public static String testsResults;
    public static final String orgTestResultInfix = "orgResult";
    public static final String patTestResultInfix = "patResult";
    public static boolean terminateByOracle;

    public static void initialize(BugWithHistory buggy, BugWithHistory org, AbstractASTParser parser) {
        if (buggy != null) {
            bugRepository = new BugRepository(buggy);
            orgRepository = new BugRepository(org);
            orgRepository.switchToOrgAndClean();
            generationOutput = ConfigurationProperties.getProperty("resultOutput") + File.separator
                    + buggy.getBugName() + File.separator + "generatedTests";
            testsResults = ConfigurationProperties.getProperty("resultOutput") + File.separator
                    + buggy.getBugName() + File.separator + "FailingTests";

            File gen = new File(generationOutput);
            FileUtils.removeFile(gen);
            gen.mkdirs();
            File test = new File(testsResults);
            FileUtils.removeFile(test);
            test.mkdirs();
        }
        ASTExtractor astExtractor = new ASTExtractor(parser);
        constructHelper = new ConstructHelper(astExtractor);
        terminateByOracle = true;
    }

    public ProjectPreparation projectPreparation;
    public AbstractCreatorHelper creatorHelper;

    public Runner(ProjectPreparation projectPreparation) {
        this.projectPreparation = projectPreparation;
    }

    public abstract void mutateTests(Skeleton skeleton);

    public abstract boolean run();


    public Map<String, List<String>> getTestsByClazz() {
        String[] tests = ConfigurationProperties.getProperty("testInfos").split("#");
        Map<String, List<String>> testsByClazz = constructHelper.getTestInfos(tests);
        return testsByClazz;
    }

    public List<Skeleton> getTestsSkeletons() {
        List<Skeleton> res = new ArrayList<>();
        Map<String, List<String>> testsByClazz = this.getTestsByClazz();
        for (Map.Entry<String, List<String>> entry :testsByClazz.entrySet()) {
            String clazzName = entry.getKey();
            String filePath = projectPreparation.srcTestDir + File.separator +
                    clazzName.replace(".", File.separator) + ".java";

            logger.info("For Test Class " + filePath + " --------------------");
            CompilationUnit compilationUnit = constructHelper.ASTExtractor.getCompilationUnit(filePath);
            logger.info("...Creating Skeleton");
            String[] s = clazzName.split("\\.");
//            Skeleton skeleton = new Skeleton(filePath, compilationUnit, s[s.length - 1]);
            List<Input> inputs = constructHelper.getOriginalTestsInputs(compilationUnit, entry.getValue());
            Skeleton skeleton = constructHelper.createASkeleton(filePath, s[s.length - 1], inputs);
            if (skeleton == null) {
                logger.error("No test candidate was constructed!");
                continue;
            }
            res.add(skeleton);
            logger.info("Finishing one Test Class --------------------");
        }
        return res;
    }

}
