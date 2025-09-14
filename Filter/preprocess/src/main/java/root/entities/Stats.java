package root.entities;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import root.util.FileUtils;

import java.util.HashMap;
import java.util.Map;

public class Stats {
    private static final Logger logger = LoggerFactory.getLogger(Stats.class);
    public static int counter = 0;

    public enum General {
        INITIALIZATION_TIME, DIFF_TIME, GENERATION_TIME, VALIDATION_TIME, TOTAL_TIME, SLICING_MODE,
        PATH_FLOW,
        GENERATED_TESTS, COMPILED_MUTANTS, FAILED_MUTANTS
    }

    public enum Patch_stat {
        ABSPATH,
        GENUINE, CORRECTNESS,
        DIFF, PATH_FLOW,
        RESULT
    }

    private static Stats currentStats;
    Map<General, Object> generalStats;
    Map<String, PatchStats> patchStats;

    Stats() {
        generalStats = new HashMap<>();
        patchStats = new HashMap<>();
    }

    public static Stats getCurrentStats() {
        if (currentStats == null) {
            currentStats = new Stats();
        }
        return currentStats;
    }

    public void addGeneralStat(General item, Object value) {
        getCurrentStats().generalStats.put(item, value);
    }

    public void addPatchStat(String patchName, Patch_stat item, Object value) {
        if (!getCurrentStats().patchStats.containsKey(patchName)) {
            getCurrentStats().patchStats.put(patchName, new PatchStats(patchName));
        }
        PatchStats stats = getCurrentStats().patchStats.get(patchName);
        stats.addStats(item, value);
    }

    public Map<General, Object> getGeneralStats() {
        return generalStats;
    }

    public Map<String, PatchStats> getPatchStats() {
        return patchStats;
    }

    @Override
    public String toString() {
        StringBuilder stringBuilder = new StringBuilder("{");
        try {
            for (Map.Entry<String, PatchStats> entry : patchStats.entrySet()) {
                stringBuilder.append(entry.getKey()).append(":").append(entry.getValue().toString()).append(",");
            }
        } catch(Exception e) {
            logger.error("Error in parse output string: {}", e.getMessage());
        }
        if (stringBuilder.length() > 1) {
            stringBuilder.replace(stringBuilder.length() - 1, stringBuilder.length(), "}");
        } else {
            stringBuilder.append("}");
        }

        String uglyJsonStr = "{" +
                "generalStats: " + FileUtils.bean2Json(generalStats) + "," +
                "patchStats:" + stringBuilder +
                '}';
        return FileUtils.jsonFormatter(uglyJsonStr);
    }

    public static class PatchStats {
        String name;
        Map<Patch_stat, Object> stats;

        public PatchStats(String name) {
            this.name = name;
            stats = new HashMap<>();
        }

        public void addStats(Patch_stat stat, Object value) {
            stats.put(stat, value);
        }

        @Override
        public String toString() {
            if (!stats.containsKey(Patch_stat.DIFF)) {
                return FileUtils.bean2Json(stats);
            } else {
                Object remove = stats.remove(Patch_stat.DIFF);
                String uglyJsonStr = FileUtils.bean2Json(stats).replace("}", "") +
                        "," +
                        "diff:" + remove.toString() +
                        '}';
                return FileUtils.jsonFormatter(uglyJsonStr);
            }
        }
    }
}
