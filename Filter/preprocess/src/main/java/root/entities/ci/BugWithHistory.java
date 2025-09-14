package root.entities.ci;

import com.google.gson.annotations.SerializedName;
import org.eclipse.jgit.lib.Repository;
import root.entities.benchmarks.Defects4JBug;

import java.util.List;

public class BugWithHistory {
    @SerializedName("bug_name")
    public String bugName;
    @SerializedName("derive")
    public String derive;
    @SerializedName("original_fixing_commit")
    public String originalFixingCommit;
    @SerializedName("inducing_commit")
    public String inducingCommit;
    @SerializedName("buildFiles_changed")
    public Boolean buildfilesChanged;
    @SerializedName("regression")
    public Boolean regression;
    @SerializedName("inducing_changes")
    public List<PatchDiff> inducingChanges;//不同的文件diff
    @SerializedName("inducing_type")
    public Actions inducingType;
    @SerializedName("trigger_tests")
    public List<FailedTest> triggerTests;
    @SerializedName("fixing_changes")
    public List<PatchDiff>  fixingChanges;
    @SerializedName("fixing_type")
    public Actions  fixingType;
    @SerializedName("patch_changed_mths")
    public NameList patchChangedMths;

    public String workingDir;

    public BugWithHistory() {}

    public BugWithHistory(String bugName, String derive, String originalFixingCommit, String inducingCommit) {
        this.bugName = bugName;
        this.derive = derive;
        this.originalFixingCommit = originalFixingCommit;
        this.inducingCommit = inducingCommit;
    }

    /*
    {
    "bug_name": "Cli_29",
    "derive": "defects4j",
    "original_fixing_commit": "gs51",
    "inducing_commit": "jsg1",
    "buildFiles_changed": true,
    "inducing_changes": {
	"changed_classes": {
		"qualified_names": ["xx"],
		"num": 1,
		},
	"changed_functions": {
		"qualified_names":["xx"],
		"num": 1,
		},
	"changed_lines":  {
		"qualified_names": ["xx"],
		"num": 3,
		},
	"diff": "xxx",
	},
    "inducing_type": {
	"add_classes": false,
	"add_functions": false,
	"delete_classes": false,
	"delete_functions": false,
	"line_level_operations": ["UPDATE", "INSERT"],
	"operation_types": [{"type": "insert", "from": "statement", "to": "block"}]
	},
    "trigger_tests": [{
	"test_class": "xx",
	"test_function": "xx",
	"message": "xx",
	}],
    "fixing_changes": {
	"changed_classes": {
		"qualified_names": ["xx"],
		"num": 1,
		},
	"changed_functions": {
		"qualified_names":["xx"],
		"num": 1,
		},
	"changed_lines":  {
		"qualified_names": ["xx"],
		"num": 3,
		},
	"diff": "xxx",
	},
    "fixing_type": {
	"add_classes": false,
	"add_functions": false,
	"delete_classes": false,
	"delete_functions": false,
	"line_level_operations": ["UPDATE", "INSERT"],
	"operations": [{"type": "insert", "from": "statement", "to": "block"}]
	}
}
    * */

    public String getWorkingDir() {
        if (this instanceof Defects4JBug) {
            return this.getWorkingDir();
        }
        return workingDir;
    }

    public String getBugName() {
        return bugName;
    }

    public void setBugName(String bugName) {
        this.bugName = bugName;
    }

    public String getDerive() {
        return derive;
    }

    public void setDerive(String derive) {
        this.derive = derive;
    }

    public String getOriginalFixingCommit() {
        return originalFixingCommit;
    }

    public void setOriginalFixingCommit(String originalFixingCommit) {
        this.originalFixingCommit = originalFixingCommit;
    }

    public String getInducingCommit() {
        return inducingCommit;
    }

    public void setInducingCommit(String inducingCommit) {
        this.inducingCommit = inducingCommit;
    }

    public Boolean getRegression() {
        return regression;
    }

    public void setRegression(Boolean regression) {
        this.regression = regression;
    }

    public Boolean getBuildfilesChanged() {
        return buildfilesChanged;
    }

    public void setBuildfilesChanged(Boolean buildfilesChanged) {
        this.buildfilesChanged = buildfilesChanged;
    }

    public List<PatchDiff> getInducingChanges() {
        return inducingChanges;
    }

    public void setInducingChanges(List<PatchDiff> inducingChanges) {
        this.inducingChanges = inducingChanges;
    }

    public List<FailedTest> getTriggerTests() {
        return triggerTests;
    }

    public void setTriggerTests(List<FailedTest> triggerTests) {
        this.triggerTests = triggerTests;
    }

    public List<PatchDiff> getFixingChanges() {
        return fixingChanges;
    }

    public void setFixingChanges(List<PatchDiff> fixingChanges) {
        this.fixingChanges = fixingChanges;
    }

    public Actions getInducingType() {
        return inducingType;
    }

    public void setInducingType(Actions inducingType) {
        this.inducingType = inducingType;
    }

    public Actions getFixingType() {
        return fixingType;
    }

    public void setFixingType(Actions fixingType) {
        this.fixingType = fixingType;
    }

    public NameList getPatchChangedMths() {
        return patchChangedMths;
    }

    public void setPatchChangedMths(NameList patchChangedMths) {
        this.patchChangedMths = patchChangedMths;
    }

    public Repository getGitRepository() {
        return null;
    }

    public boolean compile() {
        return false;
    }
}
