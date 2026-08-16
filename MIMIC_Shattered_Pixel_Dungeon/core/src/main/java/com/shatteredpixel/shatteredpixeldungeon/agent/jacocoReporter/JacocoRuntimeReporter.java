package com.shatteredpixel.shatteredpixeldungeon.agent.jacocoReporter;

import com.shatteredpixel.shatteredpixeldungeon.utils.GLog;
import io.github.cdimascio.dotenv.Dotenv;
import org.jacoco.core.data.ExecutionData;
import org.jacoco.core.data.SessionInfo;
import org.jacoco.core.tools.ExecDumpClient;
import org.jacoco.core.tools.ExecFileLoader;
import org.json.JSONObject;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.List;

/**
 * Game-side runtime reporter.
 * Each dumpData(...) call does both:
 * 1) append one action/event row into JSONL,
 * 2) write next cumulative JaCoCo exec snapshot.
 */
public final class JacocoRuntimeReporter {

    private static final Dotenv DOTENV = Dotenv.configure()
            .directory("../../")
            .filename(".env")
            .load();

    private static final String AGENT_NAME = getRequiredEnv("AGENT_NAME");

    private static final String JSONL_OUTPUT_PATH = getEnvOrDefault(
            "JACOCO_ACTION_JSONL",
            "../../out/SPD/jacoco-reports-action-jsonl/" + AGENT_NAME + "_actions.jsonl"
    );

    private static final String EXEC_OUTPUT_DIR = getEnvOrDefault(
            "JACOCO_EXEC_DIR",
            "../../out/SPD/jacoco-reports/" + AGENT_NAME
    );

    private static final String JACOCO_AGENT_HOST = getEnvOrDefault("JACOCO_AGENT_HOST", "localhost");
    private static final int JACOCO_AGENT_PORT = parseRequiredIntEnvWithDefault("JACOCO_AGENT_PORT", 6300);

    private static final DateTimeFormatter DATE_FORMAT = DateTimeFormatter.ofPattern("yy_MM_dd");

    // Timestamp origin is Jan 1st 00:00:00 of the current year (local timezone).
    private static long yearStartMillis = -1L;
    private static int cachedYear = -1;

    // Keep only the latest cumulative snapshot to merge with the next delta.
    private static File lastCumulativeExecFile = null;

    private JacocoRuntimeReporter() {
    }

    public static final class DumpResult {
        public final String execPath;
        public final String jsonlPath;
        public final long currentTimestamp;

        public DumpResult(String execPath, String jsonlPath, long currentTimestamp) {
            this.execPath = execPath;
            this.jsonlPath = jsonlPath;
            this.currentTimestamp = currentTimestamp;
        }
    }

    /**
     * Dumps current JaCoCo data (delta), creates the next cumulative snapshot,
     * and records action metadata into JSONL.
     * Handles IOException internally with up to 3 retry attempts.
     */
    public static synchronized DumpResult dumpData(int actionCounter, String action, String env) {
        final int maxRetries = 3;
        IOException lastException = null;

        for (int attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                long currentTimestamp = currentTimestampSinceYearStartMillis();
                appendActionJsonl(actionCounter, action, env, currentTimestamp);

                String date = LocalDate.now().format(DATE_FORMAT);
                String baseName = AGENT_NAME + "_" + date + "_" + currentTimestamp;

                File execDir = new File(EXEC_OUTPUT_DIR);
                ensureDirectory(execDir);

                File deltaExec = new File(execDir, baseName + "_delta.exec");
                File cumulativeExec = new File(execDir, baseName + ".exec");

                ExecFileLoader currentLoader = dumpCurrentExec(deltaExec, true);
                mergeWithPreviousCumulative(currentLoader, cumulativeExec);

                if (!deltaExec.delete()) {
                    System.err.println("Warning: failed to delete delta exec file: " + deltaExec.getAbsolutePath());
                }

                lastCumulativeExecFile = cumulativeExec;
                DumpResult result = new DumpResult(cumulativeExec.getAbsolutePath(), JSONL_OUTPUT_PATH, currentTimestamp);

                // Log dump result to console
                GLog.cov("========================== Action #" + actionCounter + " Dumped ==========================");
                GLog.cov("Action: " + action);
                GLog.cov("Environment: " + env);
                GLog.cov("Exec Path: " + result.execPath);
                GLog.cov("JSONL Path: " + result.jsonlPath);
                GLog.cov("Timestamp: " + result.currentTimestamp);
                GLog.cov("==========================================================================================");
                
                return result;

            } catch (IOException e) {
                lastException = e;
                System.err.println("Failed to dump JaCoCo data (attempt " + attempt + "/" + maxRetries + "): " + e.getMessage());
                if (attempt < maxRetries) {
                    try {
                        Thread.sleep(100 * attempt); // Brief exponential backoff
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            }
        }

        // All retries failed
        throw new RuntimeException("Failed to dump JaCoCo data after " + maxRetries + " attempts", lastException);
    }

    /**
     * Convenience overload when action metadata is unavailable.
     */
    public static synchronized DumpResult dumpData() {
        return dumpData(-1, "", "");
    }

    private static ExecFileLoader dumpCurrentExec(File execFile, boolean resetAfterDump) throws IOException {
        ExecDumpClient client = new ExecDumpClient();
        client.setDump(true);
        client.setReset(resetAfterDump);

        ExecFileLoader loader = client.dump(JACOCO_AGENT_HOST, JACOCO_AGENT_PORT);

        try (FileOutputStream fos = new FileOutputStream(execFile)) {
            loader.save(fos);
        }

        return loader;
    }

    private static void mergeWithPreviousCumulative(ExecFileLoader currentLoader, File cumulativeExec) throws IOException {
        ExecFileLoader cumulativeLoader = new ExecFileLoader();

        if (lastCumulativeExecFile != null && lastCumulativeExecFile.exists()) {
            try (FileInputStream fis = new FileInputStream(lastCumulativeExecFile)) {
                cumulativeLoader.load(fis);
            }
        }

        for (ExecutionData data : currentLoader.getExecutionDataStore().getContents()) {
            cumulativeLoader.getExecutionDataStore().put(data);
        }

        List<SessionInfo> infos = cumulativeLoader.getSessionInfoStore().getInfos();
        infos.addAll(currentLoader.getSessionInfoStore().getInfos());

        try (FileOutputStream fos = new FileOutputStream(cumulativeExec)) {
            cumulativeLoader.save(fos);
        }
    }

    private static void appendActionJsonl(int actionCounter, String action, String env, long currentTimestamp) throws IOException {
        File jsonlFile = new File(JSONL_OUTPUT_PATH);
        File parent = jsonlFile.getParentFile();
        if (parent != null) {
            ensureDirectory(parent);
        }

        JSONObject row = new JSONObject();
        row.put("actionCounter", actionCounter);
        row.put("action", action == null ? "" : action);
        row.put("env", env == null ? "" : env);
        row.put("currenttimestamp", currentTimestamp);

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(jsonlFile, true))) {
            writer.write(row.toString());
            writer.newLine();
        }
    }

    private static void ensureDirectory(File dir) throws IOException {
        if (!dir.exists() && !dir.mkdirs()) {
            throw new IOException("Failed to create directory: " + dir.getAbsolutePath());
        }
    }

    private static String getRequiredEnv(String key) {
        String value = DOTENV.get(key);
        if (value == null || value.trim().isEmpty()) {
            throw new IllegalStateException("Missing required env var: " + key + " in ../../.env");
        }
        return value;
    }

    private static String getEnvOrDefault(String key, String defaultValue) {
        String value = DOTENV.get(key);
        if (value == null || value.trim().isEmpty()) {
            return defaultValue;
        }
        return value;
    }

    private static int parseRequiredIntEnvWithDefault(String key, int defaultValue) {
        String value = DOTENV.get(key);
        if (value == null || value.trim().isEmpty()) {
            return defaultValue;
        }
        try {
            return Integer.parseInt(value.trim());
        } catch (NumberFormatException e) {
            throw new IllegalStateException("Invalid integer env var " + key + ": " + value, e);
        }
    }

    private static long currentTimestampSinceYearStartMillis() {
        LocalDate today = LocalDate.now();
        int year = today.getYear();

        // Recompute when process starts or when the year rolls over.
        if (yearStartMillis < 0L || cachedYear != year) {
            LocalDateTime startOfYear = LocalDate.of(year, 1, 1).atStartOfDay();
            yearStartMillis = startOfYear.atZone(ZoneId.systemDefault()).toInstant().toEpochMilli();
            cachedYear = year;
        }

        return System.currentTimeMillis() - yearStartMillis;
    }
}
