package root.entities.ci;

import org.eclipse.jgit.lib.Repository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import root.analysis.soot.SootUpAnalyzer;
import root.entities.benchmarks.Defects4JBug;
import root.entities.Patch;
import root.util.ConfigurationProperties;
import root.util.FileUtils;
import root.util.GitAccess;
import root.util.GitTool;

import java.io.File;
import java.util.List;

public class BugRepository implements GitAccess {

    private final Logger logger = LoggerFactory.getLogger(BugRepository.class);
    BugWithHistory bug;
    Repository repository;

    public BugRepository(BugWithHistory bug) {
        this.bug = bug;
//        bug.setBugName(bug.getProj() + "_" + bug.getId());
        this.repository = bug.getGitRepository();
        this.bug.compile();
    }

//    public void resetAnalyzer(String version) {
//        if (version.startsWith("o")) {
//            switchToOrg();
//        } else if (version.startsWith("i")) {
//            switchToInducing();
//        } else {
//            switchToBug();
//        }
//        analyzer.reset();
//    }

    public GitTool getGitAccess() {
        return gitAccess;
    }

    public Repository getRepository() {
        return repository;
    }

    public BugWithHistory getBug() {
        return bug;
    }

    public boolean test(String testName) {
        boolean res = false;
        if (!(bug instanceof Defects4JBug))
            return res;
        Defects4JBug defects4JBug = (Defects4JBug) bug;
        res = defects4JBug.specifiedTest(testName);
        return res;
    }

    public List<String> testWithRes(String testName) {
        List<String> res = null;
        if (!(bug instanceof Defects4JBug))
            return res;
        Defects4JBug defects4JBug = (Defects4JBug) bug;
        res = defects4JBug.specifiedTestWithRes(testName);
        return res;
    }

    public List<String> testRelevantWithRes(String testClass) {
        List<String> res = null;
        if (!(bug instanceof Defects4JBug))
            return res;
        Defects4JBug defects4JBug = (Defects4JBug) bug;
        res = defects4JBug.specifiedTestClassWithRes(testClass);
        return res;
    }

    public boolean compile() {
        return bug.compile();
    }

    public boolean switchToBug() {
        boolean res = false;
        if (!(bug instanceof Defects4JBug))
            return res;
        Defects4JBug defects4JBug = (Defects4JBug) bug;
        try {
            logger.info("Switch " + defects4JBug.getWorkingDir() + " to buggy commit D4J_" + defects4JBug.getProj() + "_" + defects4JBug.getId() + "_BUGGY_VERSION");
            res = gitAccess.checkoutf(defects4JBug.getWorkingDir(), defects4JBug.getD4JBuggy());
        } catch (Exception e) {
            logger.error(e.getMessage());
        }
        return res;
    }

    public boolean switchToOrg() {
        boolean res = false;
        if (!(bug instanceof Defects4JBug))
            return res;
        Defects4JBug defects4JBug = (Defects4JBug) bug;
        logger.debug("Switch to original commit  " + defects4JBug.getOriginalCommit());
        res = defects4JBug.switchTo(repository, defects4JBug.getOriginalCommit(), "org", false);
        return res;
    }

    public boolean switchToOrgAndClean() {
        boolean res = false;
        if (!(bug instanceof Defects4JBug))
            return res;
        Defects4JBug defects4JBug = (Defects4JBug) bug;
        logger.debug("Switch to original commit and test... in " + defects4JBug.getOriginalCommit());
        res = defects4JBug.switchAndClean(repository, defects4JBug.getOriginalCommit(), "org", "D4J_" + defects4JBug.getBugName().toUpperCase() + "_ORG_VERSION");
        return res;
    }

    public boolean switchToInducing() {
        boolean res = false;
        if (!(bug instanceof Defects4JBug))
            return res;
        Defects4JBug defects4JBug = (Defects4JBug) bug;
        logger.debug("Switch to inducing commit " + defects4JBug.getInducingCommit());
        res = defects4JBug.switchTo(repository, defects4JBug.getInducingCommit(), "inducing", false);
        return res;
    }

    public boolean applyPatch(Patch patch) {
//        boolean res = switchToBug();
//        if (!res) {
//            logger.error("Error occurred when switching " + bug.getBugName() + " to buggy version!");
//            return res;
//        }
        //another better way to apply patch!
        String bugRoot = this.getBug().getWorkingDir();
        String srcSubPath = patch.getPatchAbsPath().replace(patch.getPathFromRoot(), "");
        FileUtils.copy(new File(bugRoot + srcSubPath), new File(bugRoot + srcSubPath + ".bak"));
        String patchDir = bugRoot;//ConfigurationProperties.getProperty("patchDir") + File.separator;
        String[] cmd = new String[]{"/bin/bash", "-c", "cp -r "+ patch.getPathFromRoot() + File.separator + "* " + patchDir};
        int r = FileUtils.executeCommand(cmd, null, 300, null);
        return r == 0;
    }

    public void restore(Patch patch) {
        String bugRoot = this.getBug().getWorkingDir();
        String srcSubPath = patch.getPatchAbsPath().replace(patch.getPathFromRoot(), "");
        FileUtils.copy(new File(bugRoot + srcSubPath + ".bak"), new File(bugRoot + srcSubPath));
    }
}
